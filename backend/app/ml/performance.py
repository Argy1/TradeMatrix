"""Track-record numbers from stored predictions and outcomes (docs/04 definitions).

Every number here comes from real, resolved predictions, never from a backtest (docs/06).
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

LOW_SAMPLE = 100  # below this many resolved predictions the numbers are flagged as unreliable


@dataclass(frozen=True)
class Resolved:
    p_up: float
    label: str  # up / down / neutral
    actual: str  # up / down
    prev_up: bool | None  # direction of the base candle itself (for the naive baseline)


def performance(rows: Sequence[Resolved]) -> dict:
    n = len(rows)
    if n == 0:
        return {
            "n_resolved": 0, "coverage": None, "accuracy": None,
            "baseline": {"naive": None, "always_up": None},
            "brier": None, "brier_baseline": None,
            "by_label": {"up": {"n": 0, "accuracy": None}, "down": {"n": 0, "accuracy": None}},
            "low_sample": True,
        }  # fmt: skip
    y = np.array([r.actual == "up" for r in rows], dtype=float)
    p = np.array([r.p_up for r in rows], dtype=float)
    called = [r for r in rows if r.label != "neutral"]
    naive_rows = [r for r in rows if r.prev_up is not None]

    def share_correct(subset: Sequence[Resolved]) -> float | None:
        return sum(r.label == r.actual for r in subset) / len(subset) if subset else None

    by_label = {
        side: {"n": len(s), "accuracy": share_correct(s)}
        for side in ("up", "down")
        for s in [[r for r in called if r.label == side]]
    }
    base_rate = float(y.mean())
    return {
        "n_resolved": n,
        "coverage": len(called) / n,  # share of Up/Down calls; Neutral is "no call"
        "accuracy": share_correct(called),  # only Up/Down calls count
        "baseline": {
            "naive": (
                sum((r.actual == "up") == r.prev_up for r in naive_rows) / len(naive_rows)
                if naive_rows
                else None
            ),
            "always_up": base_rate,
        },
        "brier": float(np.mean((p - y) ** 2)),
        "brier_baseline": float(np.mean((base_rate - y) ** 2)),
        "by_label": by_label,
        "low_sample": n < LOW_SAMPLE,
    }
