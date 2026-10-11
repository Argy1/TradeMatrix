"""Compare the candidate settings on the development window only.

    uv run python -m app.ml.tune                      # 1h, 4h, 1d
    uv run python -m app.ml.tune 1m,3m,5m,15m,30m     # fast sizes (from the history files)

The score is the Brier improvement over the base rate (probability quality), averaged over
coins. The test folds used here all end before the evaluation period starts (config.py), so
that period plays no part in the choice. Write the winner into CHOSEN in config.py.
"""

import asyncio
import sys
from datetime import UTC, datetime

import numpy as np

from app import db
from app.ml.backtest import (
    REPORTS_DIR,
    active_assets,
    evaluate,
    load_jobs,
    summarize,
    summarize_coins,
)
from app.ml.config import candidates, dev_window, is_fast

# The coins the frozen settings were chosen on (2026-10-03). Coins added later reuse those
# settings; re-tuning on them would need a new development window.
TUNING_SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
# Fast sizes (2026-10-11): two large coins, one mid-size, one with a low price and many flat
# one-minute candles. Four are enough to choose between three candidates and keep it quick.
FAST_TUNING_SYMBOLS = ["BTC", "ETH", "SOL", "DOGE"]


async def tune(timeframes: list[str]) -> list[dict]:
    rows = []
    try:
        assets = await active_assets()
        for timeframe in timeframes:
            symbols = FAST_TUNING_SYMBOLS if is_fast(timeframe) else TUNING_SYMBOLS
            ids = {s: assets[s].id for s in symbols}
            test_from, test_until = dev_window(timeframe)
            loaded: dict[tuple, list] = {}  # candidates that share features share the data
            for config in candidates(timeframe):
                key = (config.quiet_safe, config.extended, config.pooled)
                if key not in loaded:
                    loaded[key] = await load_jobs(symbols, timeframe, config)
                summaries, n_folds = [], 0
                for _name, preds, folds in await evaluate(
                    loaded[key], timeframe, config, test_from, test_until
                ):
                    n_folds = len(folds)
                    if config.pooled and is_fast(timeframe):
                        # Scored coin by coin, so it compares like for like with the others.
                        summaries += list(summarize_coins(preds, timeframe, ids).values())
                    else:
                        summaries.append(summarize(preds, folds, timeframe))
                row = {
                    "timeframe": timeframe,
                    "config": config.name,
                    "folds": n_folds,
                    "brier_gain": float(
                        np.mean([s["brier_edge_vs_base_rate"][0] for s in summaries])
                    ),
                    "acc_edge": float(
                        np.nanmean([s["accuracy_edge_vs_naive"][0] for s in summaries])
                    ),
                    "best_edge": float(
                        np.nanmean([s["accuracy_edge_vs_best"][0] for s in summaries])
                    ),
                    "coverage": float(np.mean([s["model"]["coverage"] for s in summaries])),
                }
                rows.append(row)
                print(
                    f"{timeframe:3} {config.name:20} folds={row['folds']:3} "
                    f"brier_gain={row['brier_gain']:+.5f} acc_edge={row['acc_edge'] * 100:+.2f}pp "
                    f"vs_best={row['best_edge'] * 100:+.2f}pp "
                    f"coverage={row['coverage'] * 100:.1f}%",
                    flush=True,
                )
    finally:
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
    return rows


def write_tuning_report(rows: list[dict]) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    fast = all(is_fast(r["timeframe"]) for r in rows)
    lines = [
        f"# Tuning on the development window ({stamp})",
        "",
        "Only test folds inside the development window of each size (config.py). Score: Brier "
        "improvement over the base rate (positive = better probabilities), averaged over coins.",
        "",
        "| Timeframe | Settings | Folds | Brier gain | Accuracy minus naive | "
        "Accuracy minus best simple rule | Coverage |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['timeframe']} | {r['config']} | {r['folds']} | {r['brier_gain']:+.5f} | "
            f"{r['acc_edge'] * 100:+.2f} pp | {r['best_edge'] * 100:+.2f} pp | "
            f"{r['coverage'] * 100:.1f}% |"
        )
    lines += ["", "Best per timeframe (highest Brier gain):", ""]
    for timeframe in dict.fromkeys(r["timeframe"] for r in rows):
        best = max((r for r in rows if r["timeframe"] == timeframe), key=lambda r: r["brier_gain"])
        lines.append(f"- {timeframe}: `{best['config']}` ({best['brier_gain']:+.5f})")
    name = f"tuning_fast_{stamp}.md" if fast else f"tuning_{stamp}.md"
    (REPORTS_DIR / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    timeframes = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1h", "4h", "1d"]
    write_tuning_report(asyncio.run(tune(timeframes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
