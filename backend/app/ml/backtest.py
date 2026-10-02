"""Walk-forward backtest and report.

    uv run python -m app.ml.backtest                         # all coins, 1h and 4h, plus pooled 1d
    uv run python -m app.ml.backtest --symbols BTC --timeframes 1h

Writes backend/reports/backtest_<symbol>_<tf>_<date>.md (+ a CSV of every out-of-sample
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
from app.data import repo
from app.features.build import build_dataset, feature_columns
from app.ml import metrics
from app.ml.config import EMBARGO, NEUTRAL_HIGH, NEUTRAL_LOW, PERIODS_PER_YEAR, WINDOWS
from app.ml.train import fit_calibrated
from app.ml.walkforward import walk_forward

REPORTS_DIR = BACKEND_DIR / "reports"


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


async def load_datasets(symbols: list[str], timeframe: str) -> dict[str, pd.DataFrame]:
    factory = db.session_factory()
    async with factory() as session:
        assets = {a.symbol: a for a in await repo.list_assets(session)}
    btc = await load_candles(assets["BTC"].id, timeframe)
    datasets = {}
    for symbol in symbols:
        candles = btc if symbol == "BTC" else await load_candles(assets[symbol].id, timeframe)
        datasets[symbol] = build_dataset(candles, None if symbol == "BTC" else btc)
    return datasets


def run_walk_forward(data: pd.DataFrame, timeframe: str) -> tuple[pd.DataFrame, list[dict]]:
    """Out-of-sample predictions for every test fold, plus per-fold numbers."""
    features = feature_columns(data)
    folds = walk_forward(data.index, **WINDOWS[timeframe], embargo=EMBARGO)
    predictions, fold_rows, importances = [], [], []
    for fold in folds:
        train, test = data.iloc[fold.train], data.iloc[fold.test]
        model = fit_calibrated(
            train, data.iloc[fold.early_stop], data.iloc[fold.calibrate], features
        )
        p = model.predict(test)
        y, prev_up = test["label"].to_numpy(), test["prev_up"].to_numpy()
        base_rate = float(train["label"].mean())
        result = metrics.classification(p, y)
        fold_rows.append(
            {
                "fold": fold.number,
                "test_start": test.index.min(),
                "test_end": test.index.max(),
                "trees": int(model.booster.best_iteration + 1),
                "coverage": result["coverage"],
                "accuracy": result["accuracy"],
                "naive": float((prev_up == y).mean()),
                "brier": result["brier"],
                "brier_base_rate": metrics.brier(np.full(len(y), base_rate), y),
            }
        )
        importances.append(model.importances())
        predictions.append(
            pd.DataFrame(
                {
                    "p_up": p,
                    "label": y,
                    "prev_up": prev_up,
                    "next_return": test["next_return"].to_numpy(),
                    "base_rate": base_rate,
                    "fold": fold.number,
                    **({"asset_id": test["asset_id"].to_numpy()} if "asset_id" in test else {}),
                },
                index=test.index,
            )
        )
    preds = pd.concat(predictions) if predictions else pd.DataFrame()
    preds.attrs["importances"] = pd.DataFrame(importances).mean().sort_values(ascending=False)
    return preds, fold_rows


def summarize(preds: pd.DataFrame, fold_rows: list[dict], timeframe: str) -> dict:
    p, y = preds["p_up"].to_numpy(), preds["label"].to_numpy()
    prev_up = preds["prev_up"].to_numpy()
    model = metrics.classification(p, y)
    base = metrics.baselines(prev_up, y, base_rate=float(preds["base_rate"].mean()))
    base["brier_base_rate"] = metrics.brier(preds["base_rate"].to_numpy(), y)

    folds = pd.DataFrame(fold_rows)
    with_calls = folds.dropna(subset=["accuracy"])
    acc_edge = metrics.bootstrap_ci((with_calls["accuracy"] - with_calls["naive"]).to_numpy())
    brier_edge = metrics.bootstrap_ci((folds["brier_base_rate"] - folds["brier"]).to_numpy())
    beats = acc_edge[1] > 0 and brier_edge[1] > 0 and model["accuracy"] is not None

    # The strategy is simulated per coin in time order (pooled 1d rows are split by coin).
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
        "brier_edge_vs_base_rate": brier_edge,
        "beats_baselines": beats,
        "strategy": strategy,
        "reliability": metrics.reliability_table(p, y),
        "folds": folds,
        "importances": preds.attrs["importances"],
        "period": (preds.index.min(), preds.index.max()),
    }


def _pct(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None or np.isnan(value) else f"{value * 100:.{digits}f}%"


def write_report(name: str, timeframe: str, summary: dict, preds: pd.DataFrame) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    path = REPORTS_DIR / f"backtest_{name}_{timeframe}_{stamp}.md"
    preds.to_csv(path.with_suffix(".csv"))
    m, b, s = summary["model"], summary["baselines"], summary["strategy"]
    acc, brier = summary["accuracy_edge_vs_naive"], summary["brier_edge_vs_base_rate"]
    start, end = summary["period"]
    verdict = (
        "The model beats both baselines, and the 95% interval of the edge stays above zero."
        if summary["beats_baselines"]
        else "The model does NOT beat the baselines with a margin that survives the bootstrap "
        "check. Treat its signals as no better than the simple rules below."
    )
    lines = [
        f"# Backtest {name} {timeframe} ({stamp})",
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
        f"always-up {_pct(b['always_up'])} |",
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
        lines.append(
            f"| {f.fold} | {f.test_start:%Y-%m-%d} to {f.test_end:%Y-%m-%d} | {f.trees} | "
            f"{_pct(f.coverage)} | {_pct(f.accuracy)} | {_pct(f.naive)} | {f.brier:.4f} | "
            f"{f.brier_base_rate:.4f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


async def run(symbols: list[str], timeframes: list[str]) -> list[tuple[str, str, dict, Path]]:
    results = []
    try:
        for timeframe in timeframes:
            datasets = await load_datasets(symbols, timeframe)
            if timeframe == "1d":
                # Too few daily candles per coin, so one model learns from all coins together.
                pooled = pd.concat(
                    [d.assign(asset_id=float(i)) for i, d in enumerate(datasets.values())]
                ).sort_index(kind="stable")
                jobs = [("ALL", pooled)]
            else:
                jobs = list(datasets.items())
            for name, data in jobs:
                preds, fold_rows = await asyncio.to_thread(run_walk_forward, data, timeframe)
                summary = summarize(preds, fold_rows, timeframe)
                path = write_report(name, timeframe, summary, preds)
                results.append((name, timeframe, summary, path))
                m, b = summary["model"], summary["baselines"]
                print(
                    f"{name:4} {timeframe:3} acc={_pct(m['accuracy'])} cov={_pct(m['coverage'])} "
                    f"naive={_pct(b['naive'])} brier={m['brier']:.4f} "
                    f"base={b['brier_base_rate']:.4f} "
                    f"beats={summary['beats_baselines']} -> {path.name}"
                )
    finally:
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Walk-forward backtest with honest baselines.")
    parser.add_argument("--symbols", default="BTC,ETH,SOL,BNB,XRP")
    parser.add_argument("--timeframes", default="1h,4h,1d")
    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    timeframes = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    asyncio.run(run(symbols, timeframes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
