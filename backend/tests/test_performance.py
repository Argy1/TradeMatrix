"""Track-record math (docs/04 definitions)."""

import pytest

from app.ml.performance import Resolved, performance


def test_definitions() -> None:
    rows = [
        Resolved(0.70, "up", "up", True),  # call right; naive (repeat up) right
        Resolved(0.60, "up", "down", True),  # call wrong; naive wrong
        Resolved(0.30, "down", "down", False),  # call right; naive right
        Resolved(0.50, "neutral", "up", False),  # no call; naive wrong
    ]
    stats = performance(rows)
    assert stats["n_resolved"] == 4
    assert stats["coverage"] == pytest.approx(3 / 4)
    assert stats["accuracy"] == pytest.approx(2 / 3)  # Neutral does not count
    assert stats["baseline"]["naive"] == pytest.approx(2 / 4)
    assert stats["baseline"]["always_up"] == pytest.approx(2 / 4)
    y, p = [1, 0, 0, 1], [0.7, 0.6, 0.3, 0.5]
    assert stats["brier"] == pytest.approx(sum((a - b) ** 2 for a, b in zip(p, y, strict=True)) / 4)
    assert stats["brier_baseline"] == pytest.approx(0.25)
    assert stats["by_label"]["up"] == {"n": 2, "accuracy": 0.5}
    assert stats["by_label"]["down"] == {"n": 1, "accuracy": 1.0}
    assert stats["low_sample"] is True


def test_no_data_yet_is_explicit() -> None:
    stats = performance([])
    assert stats["accuracy"] is None and stats["low_sample"] is True


def test_missing_previous_candle_is_left_out_of_naive() -> None:
    stats = performance([Resolved(0.6, "up", "up", None), Resolved(0.6, "up", "up", True)])
    assert stats["baseline"]["naive"] == 1.0  # only the row that has a previous candle
