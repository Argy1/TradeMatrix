"""Compare the candidate settings on the development window only.

    uv run python -m app.ml.tune

The score is the Brier improvement over the base rate (probability quality), averaged over
coins. The test folds used here all end before DEV_UNTIL, so the final evaluation period
(EVAL_FROM onwards) plays no part in the choice. Write the winner into CHOSEN in config.py.
"""

import asyncio
import sys
from datetime import UTC, datetime

import numpy as np

from app import db
from app.ml.backtest import REPORTS_DIR, load_jobs, run_walk_forward, summarize
from app.ml.config import DEV_FROM, DEV_UNTIL, candidates

SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]


async def tune(timeframes: list[str]) -> list[dict]:
    rows = []
    try:
        for timeframe in timeframes:
            jobs = await load_jobs(SYMBOLS, timeframe)
            for config in candidates(timeframe):
                per_job = []
                for _name, data in jobs:
                    preds, folds = await asyncio.to_thread(
                        run_walk_forward, data, timeframe, config, DEV_FROM[timeframe], DEV_UNTIL
                    )
                    per_job.append((summarize(preds, folds, timeframe), len(folds)))
                row = {
                    "timeframe": timeframe,
                    "config": config.name,
                    "folds": per_job[0][1],
                    "brier_gain": float(
                        np.mean([s["brier_edge_vs_base_rate"][0] for s, _ in per_job])
                    ),
                    "acc_edge": float(
                        np.mean([s["accuracy_edge_vs_naive"][0] for s, _ in per_job])
                    ),
                    "coverage": float(np.mean([s["model"]["coverage"] for s, _ in per_job])),
                }
                rows.append(row)
                print(
                    f"{timeframe:3} {config.name:20} folds={row['folds']:3} "
                    f"brier_gain={row['brier_gain']:+.5f} acc_edge={row['acc_edge'] * 100:+.2f}pp "
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
    lines = [
        f"# Tuning on the development window ({stamp})",
        "",
        f"Test folds between DEV_FROM and {DEV_UNTIL:%Y-%m-%d} only. Score: Brier improvement over "
        "the base rate (positive = better probabilities), averaged over coins.",
        "",
        "| Timeframe | Settings | Folds | Brier gain | Accuracy minus naive | Coverage |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['timeframe']} | {r['config']} | {r['folds']} | {r['brier_gain']:+.5f} | "
            f"{r['acc_edge'] * 100:+.2f} pp | {r['coverage'] * 100:.1f}% |"
        )
    lines += ["", "Best per timeframe (highest Brier gain):", ""]
    for timeframe in dict.fromkeys(r["timeframe"] for r in rows):
        best = max((r for r in rows if r["timeframe"] == timeframe), key=lambda r: r["brier_gain"])
        lines.append(f"- {timeframe}: `{best['config']}` ({best['brier_gain']:+.5f})")
    (REPORTS_DIR / f"tuning_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    timeframes = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1h", "4h", "1d"]
    write_tuning_report(asyncio.run(tune(timeframes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
