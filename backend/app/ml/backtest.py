"""Walk-forward backtest and report.

    uv run python -m app.ml.backtest                         # all coins, 1h and 4h, plus pooled 1d
    uv run python -m app.ml.backtest --symbols BTC --timeframes 1h
    uv run python -m app.ml.backtest --timeframes 1m,3m,5m,15m,30m    # fast sizes (history files)

Writes backend/reports/backtest_<symbol>_<tf>_<date>.md (+ a file with every out-of-sample
prediction). The numbers are reported as they come out, good or bad (docs/06).
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

from app import db
from app.config import BACKEND_DIR
from app.data import history, repo
from app.features.build import build_dataset, feature_columns, labelled
from app.ml import metrics
from app.ml.config import (
    EMBARGO,
    NEUTRAL_HIGH,
    NEUTRAL_LOW,
    PERIODS_PER_YEAR,
    ModelConfig,
    chosen,
    eval_from,
    is_fast,
)
from app.ml.train import fit_calibrated
from app.ml.walkforward import walk_forward

REPORTS_DIR = BACKEND_DIR / "reports"
PARALLEL = 4  # datasets evaluated at the same time (each model fit already uses 4 threads)
_NOT_FEATURES = ("label", "next_return", "prev_up")


async def load_candles(asset_id: int, timeframe: str) -> pd.DataFrame:
    factory = db.session_factory()
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with factory() as session:
        rows = await session.execute(
            text(
                "select open_time, open, high, low, close, volume from candles "
                "where asset_id = :a and timeframe = :tf order by open_time"
            ),
            {"a": asset_id, "tf": timeframe},
        )
        frame = pd.DataFrame(
            rows.all(), columns=["open_time", "open", "high", "low", "close", "volume"]
        )
    return frame.set_index("open_time").astype("float64")


async def candles_for(asset: repo.Asset, timeframe: str) -> pd.DataFrame:
    """Fast sizes are read from the history files (app/data/history.py), the others from the
    database."""
    if is_fast(timeframe):
        return await asyncio.to_thread(history.load, asset.symbol, timeframe)
    return await load_candles(asset.id, timeframe)


async def active_assets() -> dict[str, repo.Asset]:
    """Every active coin in the assets table (the database decides which coins exist)."""
    factory = db.session_factory()
    async with factory() as session:
        return {a.symbol: a for a in await repo.list_assets(session)}


async def active_symbols() -> list[str]:
    return list(await active_assets())


def _compact(data: pd.DataFrame) -> pd.DataFrame:
    """Features as 32-bit numbers (what XGBoost uses anyway): half the memory, which matters
    with half a million one-minute rows per coin."""
    columns = [c for c in data.columns if c not in _NOT_FEATURES]
    return data.astype(dict.fromkeys(columns, "float32"))


async def load_datasets(
    symbols: list[str], timeframe: str, config: ModelConfig | None = None
) -> dict[str, pd.DataFrame]:
    config = config or chosen(timeframe)
    assets = await active_assets()
    btc = await candles_for(assets["BTC"], timeframe)
    datasets = {}
    for symbol in symbols:
        candles = btc if symbol == "BTC" else await candles_for(assets[symbol], timeframe)
        data = await asyncio.to_thread(
            build_dataset, candles, None if symbol == "BTC" else btc, **config.dataset_options
        )
        datasets[symbol] = _compact(data) if is_fast(timeframe) else data
    return datasets


async def load_jobs(
    symbols: list[str], timeframe: str, config: ModelConfig | None = None
) -> list[tuple[str, pd.DataFrame]]:
    """One dataset per coin, or one pooled dataset: always for 1d (too few daily candles per
    coin), and for a fast size when its settings say `pooled`."""
    config = config or chosen(timeframe)
    datasets = await load_datasets(symbols, timeframe, config)
    if timeframe != "1d" and not config.pooled:
        return list(datasets.items())
    ids = {symbol: asset.id for symbol, asset in (await active_assets()).items()}
    # The pooled model sees which coin a row belongs to through its database id, the same
    # value the worker passes when it predicts live.
    pooled = pd.concat(
        [d.assign(asset_id=float(ids[symbol])) for symbol, d in datasets.items()]
    ).sort_index(kind="stable")
    return [("ALL", pooled)]


def fold_metrics(frame: pd.DataFrame) -> dict:
    """The numbers of one test fold, from its predictions (columns p_up, label, prev_up,
    next_return, base_rate). Every simple rule is scored next to the model.

    Rows without a label (fast sizes: the next candle closed flat) have no result, so they
    count for coverage and for the share of flat candles, but not as right or wrong.
    """
    scored = labelled(frame)
    p, y = scored["p_up"].to_numpy(), scored["label"].to_numpy()
    prev_up = scored["prev_up"].to_numpy()
    result = metrics.classification(p, y)
    up_share = float(y.mean()) if len(y) else None
    return {
        "coverage": float((metrics.signals(frame["p_up"].to_numpy()) != 0).mean()),
        "accuracy": result["accuracy"],
        "naive": float((prev_up == y).mean()) if len(y) else None,
        "always_up": up_share,
        "always_down": None if up_share is None else 1 - up_share,
        "flat_share": float((frame["next_return"].to_numpy() == 0).mean()),
        "brier": result["brier"] if len(y) else None,
        "brier_base_rate": metrics.brier(scored["base_rate"].to_numpy(), y) if len(y) else None,
    }


def fold_rows_of(preds: pd.DataFrame) -> list[dict]:
    """Per-fold numbers rebuilt from stored predictions (used to score one coin of a pooled
    model on its own)."""
    return [
        {"fold": number, "test_start": g.index.min(), "test_end": g.index.max(), "trees": None}
        | fold_metrics(g)
        for number, g in preds.groupby("fold")
    ]


def run_walk_forward(
    data: pd.DataFrame,
    timeframe: str,
    config: ModelConfig | None = None,
    test_from: datetime | None = None,
    test_until: datetime | None = None,
) -> tuple[pd.DataFrame, list[dict]]:
    """Out-of-sample predictions for every test fold, plus per-fold numbers.

    `test_from` / `test_until` keep only folds whose test period lies inside that window, so the
    tuning script can compare settings on old data without ever touching the final test period.
    """
    config = config or chosen(timeframe)
    features = feature_columns(data)
    folds = [
        fold
        for fold in walk_forward(
            data.index, **config.windows, embargo=EMBARGO, expanding=config.expanding
        )
        if (test_from is None or data.index[fold.test].min() >= test_from)
        and (test_until is None or data.index[fold.test].max() < test_until)
    ]
    predictions, fold_rows, importances = [], [], []
    for fold in folds:
        # Training, early stopping and calibration use only rows with a result. The test
        # rows are all predicted: live, the model cannot know that a candle will be flat.
        train, test = labelled(data.iloc[fold.train]), data.iloc[fold.test]
        model = fit_calibrated(
            train,
            labelled(data.iloc[fold.early_stop]),
            labelled(data.iloc[fold.calibrate]),
            features,
            config.params,
        )
        frame = pd.DataFrame(
            {
                "p_up": model.predict(test),
                "label": test["label"].to_numpy(),
                "prev_up": test["prev_up"].to_numpy(),
                "next_return": test["next_return"].to_numpy(),
                "base_rate": float(train["label"].mean()),
                "fold": fold.number,
                **({"asset_id": test["asset_id"].to_numpy()} if "asset_id" in test else {}),
            },
            index=test.index,
        )
        fold_rows.append(
            {
                "fold": fold.number,
                "test_start": test.index.min(),
                "test_end": test.index.max(),
                "trees": int(model.booster.best_iteration + 1),
            }
            | fold_metrics(frame)
        )
        importances.append(model.importances())
        predictions.append(frame)
    preds = pd.concat(predictions) if predictions else pd.DataFrame()
    preds.attrs["importances"] = pd.DataFrame(importances).mean().sort_values(ascending=False)
    return preds, fold_rows


def summarize(preds: pd.DataFrame, fold_rows: list[dict], timeframe: str) -> dict:
    scored = labelled(preds)  # rows with a result; the strategy below uses every row
    p, y = scored["p_up"].to_numpy(), scored["label"].to_numpy()
    prev_up = scored["prev_up"].to_numpy()
    model = metrics.classification(p, y)
    model["coverage"] = float((metrics.signals(preds["p_up"].to_numpy()) != 0).mean())
    model["flat_share"] = float((preds["next_return"].to_numpy() == 0).mean())
    base = metrics.baselines(prev_up, y, base_rate=float(scored["base_rate"].mean()))
    base["brier_base_rate"] = metrics.brier(scored["base_rate"].to_numpy(), y)

    folds = pd.DataFrame(fold_rows)
    numeric = [c for c in folds.columns if c not in ("test_start", "test_end")]
    folds[numeric] = folds[numeric].astype("float64")  # None (no calls in a fold) becomes NaN
    with_calls = folds.dropna(subset=["accuracy"])
    acc_edge = metrics.bootstrap_ci((with_calls["accuracy"] - with_calls["naive"]).to_numpy())
    # The model has to beat the BEST simple rule of each fold, not only the naive one.
    best_simple = with_calls[["naive", "always_up", "always_down"]].max(axis=1)
    best_edge = metrics.bootstrap_ci((with_calls["accuracy"] - best_simple).to_numpy())
    with_result = folds.dropna(subset=["brier"])
    brier_edge = metrics.bootstrap_ci(
        (with_result["brier_base_rate"] - with_result["brier"]).to_numpy()
    )
    # "ok" needs both: more accurate than the best simple rule, and better probabilities than
    # the base rate. Each with a 95% interval above zero (NaN, when the model made no calls,
    # compares as False).
    beats = bool(best_edge[1] > 0 and brier_edge[1] > 0 and model["accuracy"] is not None)

    # The strategy is simulated per coin in time order (pooled rows are split by coin).
    groups = [g for _, g in preds.groupby("asset_id")] if "asset_id" in preds else [preds]
    periods = PERIODS_PER_YEAR[timeframe]

    def per_coin(fn) -> dict:
        stats = [fn(g) for g in groups]
        return {key: float(np.nanmean([s[key] for s in stats if s[key] is not None]))
                for key in ("total_return", "max_drawdown", "sharpe")}  # fmt: skip

    strategy = {
        "model_long_only": per_coin(lambda g: metrics.simulate_long_only(
            metrics.signals(g["p_up"].to_numpy()), g["next_return"].to_numpy(), periods)),
        "naive_long_only": per_coin(lambda g: metrics.simulate_long_only(
            g["prev_up"].to_numpy(), g["next_return"].to_numpy(), periods)),
        "buy_and_hold": per_coin(lambda g: metrics.buy_and_hold(
            g["next_return"].to_numpy(), periods)),
    }  # fmt: skip
    return {
        "model": model,
        "baselines": base,
        "accuracy_edge_vs_naive": acc_edge,
        "accuracy_edge_vs_best": best_edge,
        "brier_edge_vs_base_rate": brier_edge,
        "beats_baselines": beats,
        "strategy": strategy,
        "reliability": metrics.reliability_table(p, y),
        "folds": folds,
        "importances": preds.attrs.get("importances", pd.Series(dtype="float64")),
        "period": (preds.index.min(), preds.index.max()),
    }


def summarize_coins(preds: pd.DataFrame, timeframe: str, ids: dict[str, int]) -> dict[str, dict]:
    """A pooled model scored coin by coin: each coin keeps only its own predictions."""
    out = {}
    for symbol, asset_id in ids.items():
        own = preds[preds["asset_id"] == float(asset_id)].drop(columns="asset_id")
        if len(own):
            own.attrs["importances"] = preds.attrs.get("importances")
            out[symbol] = summarize(own, fold_rows_of(own), timeframe)
    return out


def _pct(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None or np.isnan(value) else f"{value * 100:.{digits}f}%"


def best_simple_rule(numbers: dict) -> float:
    """Accuracy of the best of: repeat the last candle, always Up, always Down."""
    return max(numbers["naive"], numbers["always_up"], 1 - numbers["always_up"])


def write_report(
    name: str,
    timeframe: str,
    summary: dict,
    preds: pd.DataFrame,
    config: ModelConfig | None = None,
) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    config = config or chosen(timeframe)
    path = REPORTS_DIR / f"backtest_{name}_{timeframe}_{stamp}_{config.name}.md"
    if is_fast(timeframe):
        preds.to_parquet(path.with_suffix(".parquet"))  # far smaller than CSV for these sizes
    else:
        preds.to_csv(path.with_suffix(".csv"))
    m, b, s = summary["model"], summary["baselines"], summary["strategy"]
    acc, brier = summary["accuracy_edge_vs_naive"], summary["brier_edge_vs_base_rate"]
    best = summary["accuracy_edge_vs_best"]
    start, end = summary["period"]
    verdict = (
        "The model beats the simple rules, and the 95% interval of the edge stays above zero."
        if summary["beats_baselines"]
        else "The model does NOT beat the baselines with a margin that survives the bootstrap "
        "check. Treat its signals as no better than the simple rules below."
    )
    if is_fast(timeframe):
        settings = (
            f"Model settings: `{config.name}` (chosen on test folds before "
            f"{eval_from(timeframe):%Y-%m-%d} only, see `reports/tuning_*.md`). The folds below "
            "start on or after that date and were scored once. A candle that closes at exactly "
            "the previous close is flat: it has no result and is counted neither right nor wrong."
        )
    else:
        settings = (
            f"Model settings: `{config.name}` (chosen on the 2021-2024 development window only, "
            f"see `reports/tuning_*.md`). Test folds start on or after "
            f"{eval_from(timeframe):%Y-%m-%d}. Note: this period was also scored once in the "
            "first run (before the improvement round), so it is not perfectly unseen."
        )
    lines = [
        f"# Backtest {name} {timeframe} ({stamp})",
        "",
        settings,
        "",
        f"Out-of-sample period: {start:%Y-%m-%d} to {end:%Y-%m-%d}, {len(summary['folds'])} "
        f"walk-forward folds, {m['n']} predictions. "
        f"Neutral band {NEUTRAL_LOW:.2f}-{NEUTRAL_HIGH:.2f}.",
        "",
        f"**Verdict:** {verdict}",
        "",
        "| Measure | Model | Baseline |",
        "| --- | --- | --- |",
        f"| Accuracy of Up/Down calls | {_pct(m['accuracy'])} | naive {_pct(b['naive'])}, "
        f"always-up {_pct(b['always_up'])}, always-down {_pct(b['always_down'])} |",
        f"| Flat candles (close equal to the previous close) | {_pct(m['flat_share'])} | |",
        f"| Coverage (share of non-neutral calls) | {_pct(m['coverage'])} | 100% |",
        f"| Brier score (lower is better) | {m['brier']:.4f} | "
        f"base rate {b['brier_base_rate']:.4f} |",
        f"| Log loss | {m['log_loss']:.4f} | coin flip {np.log(2):.4f} |",
        f"| Up calls: n / precision / recall | {m['up_n']} / {_pct(m['up_precision'])} / "
        f"{_pct(m['up_recall'])} | |",
        f"| Down calls: n / precision / recall | {m['down_n']} / {_pct(m['down_precision'])} / "
        f"{_pct(m['down_recall'])} | |",
        "",
        "Bootstrap over folds (mean, 95% interval):",
        f"- Accuracy minus naive: {_pct(acc[0], 2)} ({_pct(acc[1], 2)} to {_pct(acc[2], 2)})",
        f"- Accuracy minus the best simple rule: {_pct(best[0], 2)} ({_pct(best[1], 2)} to "
        f"{_pct(best[2], 2)})",
        f"- Brier improvement over base rate: {brier[0]:.5f} ({brier[1]:.5f} to {brier[2]:.5f})",
        "",
        "## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)",
        "",
        "| Strategy | Total return | Max drawdown | Sharpe |",
        "| --- | --- | --- | --- |",
    ]
    for label, key in (("Model (hold while Up)", "model_long_only"),
                       ("Naive (hold after an up candle)", "naive_long_only"),
                       ("Buy and hold", "buy_and_hold")):  # fmt: skip
        row = s[key]
        lines.append(f"| {label} | {_pct(row['total_return'])} | {_pct(row['max_drawdown'])} | "
                     f"{row['sharpe']:.2f} |")  # fmt: skip
    lines += ["", "## Reliability (does p mean what it says?)", "",
              "| p bucket | n | mean p | share that went up |",
              "| --- | --- | --- | --- |"]  # fmt: skip
    lines += [f"| {r['bucket']} | {r['n']} | {r['mean_p']:.3f} | {r['share_up']:.3f} |"
              for r in summary["reliability"]]  # fmt: skip
    lines += ["", "## Most useful features (average gain)", ""]
    lines += [
        f"- {feature}: {gain:.2f}" for feature, gain in summary["importances"].head(8).items()
    ]
    lines += ["", "## Folds", "",
              "| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]  # fmt: skip
    for f in summary["folds"].itertuples():
        trees = "" if np.isnan(f.trees) else f"{f.trees:.0f}"
        lines.append(
            f"| {f.fold:.0f} | {f.test_start:%Y-%m-%d} to {f.test_end:%Y-%m-%d} | {trees} | "
            f"{_pct(f.coverage)} | {_pct(f.accuracy)} | {_pct(f.naive)} | {f.brier:.4f} | "
            f"{f.brier_base_rate:.4f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def summary_line(name: str, timeframe: str, summary: dict) -> str:
    m, b = summary["model"], summary["baselines"]
    return (
        f"{name:5} {timeframe:3} acc={_pct(m['accuracy'])} cov={_pct(m['coverage'])} "
        f"best_simple={_pct(best_simple_rule(b))} flat={_pct(m['flat_share'])} "
        f"brier={m['brier']:.4f} "
        f"base={b['brier_base_rate']:.4f} beats={summary['beats_baselines']}"
    )


def write_summary_table(results: list[tuple[str, str, dict, Path]]) -> Path:
    """One row per coin and size: the page to read first."""
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    sizes = "_".join(dict.fromkeys(tf for _, tf, _, _ in results))
    path = REPORTS_DIR / f"summary_{sizes}_{stamp}.md"
    passed = sum(1 for _, _, s, _ in results if s["beats_baselines"])
    lines = [
        f"# Backtest summary ({stamp})",
        "",
        f'{passed} of {len(results)} coin-size pairs beat the simple rules. "ok" needs two '
        "things, each with a 95% interval above zero: more accurate than the best simple rule "
        "(repeat the last candle, always Up, always Down), and better probabilities than the "
        'base rate (Brier). Everything else is "degraded" and is shown in the apps with the '
        "below-baseline warning.",
        "",
        'Accuracy counts only Up/Down calls. "Calls" is the share of signals that were not '
        'Neutral. A flat candle (same close as the one before) has no result. "After fees" is '
        "the simulated return of holding the coin while the signal says Up, with 0.1% fee and "
        "0.05% slippage per trade.",
        "",
        "| Coin | Size | Result | Calls | Accuracy | Best simple rule | Accuracy edge "
        "(95% interval) | Flat candles | Brier gain (95% interval) | After fees | Buy and hold |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, timeframe, s, _ in results:
        m, b = s["model"], s["baselines"]
        brier, edge = s["brier_edge_vs_base_rate"], s["accuracy_edge_vs_best"]
        lines.append(
            f"| {name} | {timeframe} | {'ok' if s['beats_baselines'] else 'degraded'} | "
            f"{_pct(m['coverage'])} | {_pct(m['accuracy'])} | {_pct(best_simple_rule(b))} | "
            f"{_pct(edge[0], 2)} ({_pct(edge[1], 2)} to {_pct(edge[2], 2)}) | "
            f"{_pct(m['flat_share'])} | "
            f"{brier[0]:+.5f} ({brier[1]:+.5f} to {brier[2]:+.5f}) | "
            f"{_pct(s['strategy']['model_long_only']['total_return'])} | "
            f"{_pct(s['strategy']['buy_and_hold']['total_return'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


async def evaluate(
    jobs: list[tuple[str, pd.DataFrame]],
    timeframe: str,
    config: ModelConfig,
    test_from: datetime | None,
    test_until: datetime | None = None,
) -> list[tuple[str, pd.DataFrame, list[dict]]]:
    """Walk-forward for several datasets at once (XGBoost releases Python's lock while it
    trains, so threads really run side by side)."""
    gate = asyncio.Semaphore(PARALLEL)

    async def one(name: str, data: pd.DataFrame) -> tuple[str, pd.DataFrame, list[dict]]:
        async with gate:
            preds, fold_rows = await asyncio.to_thread(
                run_walk_forward, data, timeframe, config, test_from, test_until
            )
        return name, preds, fold_rows

    return list(await asyncio.gather(*(one(name, data) for name, data in jobs)))


async def run(symbols: list[str], timeframes: list[str]) -> list[tuple[str, str, dict, Path]]:
    results = []
    try:
        assets = await active_assets()
        everyone = list(assets)
        symbols = symbols or everyone
        for timeframe in timeframes:
            config = chosen(timeframe)
            # A pooled model always learns from every active coin.
            pooled = timeframe == "1d" or config.pooled
            jobs = await load_jobs(everyone if pooled else symbols, timeframe, config)
            for name, preds, fold_rows in await evaluate(
                jobs, timeframe, config, eval_from(timeframe)
            ):
                if pooled and is_fast(timeframe):
                    # One model, but every coin gets its own numbers and its own verdict.
                    ids = {s: assets[s].id for s in symbols}
                    scored = summarize_coins(preds, timeframe, ids)
                    owned = {
                        s: preds[preds["asset_id"] == float(ids[s])].drop(columns="asset_id")
                        for s in scored
                    }
                else:
                    scored, owned = {name: summarize(preds, fold_rows, timeframe)}, {name: preds}
                for coin, summary in scored.items():
                    path = write_report(coin, timeframe, summary, owned[coin], config)
                    results.append((coin, timeframe, summary, path))
                    print(f"{summary_line(coin, timeframe, summary)} -> {path.name}", flush=True)
        if any(is_fast(tf) for tf in timeframes) and results:
            print(f"summary -> {write_summary_table(results).name}", flush=True)
    finally:
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Walk-forward backtest with honest baselines.")
    parser.add_argument("--symbols", default="", help="default: every active coin")
    parser.add_argument("--timeframes", default="1h,4h,1d")
    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    timeframes = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    asyncio.run(run(symbols, timeframes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
