"""Track-record numbers from stored predictions and outcomes (docs/04 definitions).

Every number here comes from real, resolved predictions, never from a backtest (docs/06).

The numbers are built from plain counts (`Totals`). Counts can be added up, so the same maths
serves a list of single signals (the newest 200 on the signal card) and the daily counts in
`signal_stats_daily` (the track-record page), and both always agree.
"""

from collections.abc import Sequence
from dataclasses import dataclass, fields

LOW_SAMPLE = 100  # below this many resolved predictions the numbers are flagged as unreliable


@dataclass(frozen=True)
class Resolved:
    p_up: float
    label: str  # up / down / neutral
    actual: str  # up / down
    prev_up: bool | None  # direction of the base candle itself (for the naive baseline)


@dataclass(frozen=True)
class Totals:
    """Counts over signals that have a result (their candle closed up or down)."""

    n_resolved: int = 0
    n_went_up: int = 0
    n_calls: int = 0  # signals that said Up or Down; Neutral is "no call"
    n_correct: int = 0
    n_up_calls: int = 0
    n_up_correct: int = 0
    n_down_calls: int = 0
    n_down_correct: int = 0
    n_naive: int = 0  # rows where the naive rule could answer (the candle before is known)
    n_naive_correct: int = 0
    brier_sum: float = 0.0  # sum of (p_up - went_up)^2

    def __add__(self, other: "Totals") -> "Totals":
        return Totals(*(getattr(self, f.name) + getattr(other, f.name) for f in fields(self)))


def totals_of(rows: Sequence[Resolved]) -> Totals:
    def count(condition) -> int:
        return sum(1 for r in rows if condition(r))

    return Totals(
        n_resolved=len(rows),
        n_went_up=count(lambda r: r.actual == "up"),
        n_calls=count(lambda r: r.label != "neutral"),
        n_correct=count(lambda r: r.label == r.actual),
        n_up_calls=count(lambda r: r.label == "up"),
        n_up_correct=count(lambda r: r.label == "up" and r.actual == "up"),
        n_down_calls=count(lambda r: r.label == "down"),
        n_down_correct=count(lambda r: r.label == "down" and r.actual == "down"),
        n_naive=count(lambda r: r.prev_up is not None),
        n_naive_correct=count(lambda r: r.prev_up is not None and (r.actual == "up") == r.prev_up),
        brier_sum=float(sum((r.p_up - (r.actual == "up")) ** 2 for r in rows)),
    )


def _share(part: int, whole: int) -> float | None:
    return part / whole if whole else None


def from_totals(t: Totals) -> dict:
    up_rate = _share(t.n_went_up, t.n_resolved)
    naive = _share(t.n_naive_correct, t.n_naive)
    # Four one-line rules. "reverse" says the opposite of the last candle: on short candles
    # the price often bounces between two neighbouring price steps, so it can beat a coin flip.
    rules = {
        "naive": naive,
        "reverse": None if naive is None else 1 - naive,
        "always_up": up_rate,
        "always_down": None if up_rate is None else 1 - up_rate,
    }
    known = [value for value in rules.values() if value is not None]
    return {
        "n_resolved": t.n_resolved,
        "coverage": _share(t.n_calls, t.n_resolved),  # share of Up/Down calls
        "accuracy": _share(t.n_correct, t.n_calls),  # only Up/Down calls count
        # "best" is the number the model has to beat: the best of the four rules.
        "baseline": rules | {"best": max(known) if known else None},
        "brier": t.brier_sum / t.n_resolved if t.n_resolved else None,
        # Always answering the share of up candles: mean of (rate - y)^2 = rate * (1 - rate).
        "brier_baseline": None if up_rate is None else up_rate * (1 - up_rate),
        "by_label": {
            "up": {"n": t.n_up_calls, "accuracy": _share(t.n_up_correct, t.n_up_calls)},
            "down": {"n": t.n_down_calls, "accuracy": _share(t.n_down_correct, t.n_down_calls)},
        },
        "low_sample": t.n_resolved < LOW_SAMPLE,
    }


def performance(rows: Sequence[Resolved]) -> dict:
    return from_totals(totals_of(rows))
