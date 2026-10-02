"""Metrics, baselines and the walk-forward splitter."""

import itertools

import numpy as np
import pandas as pd
import pytest

from app.ml import metrics
from app.ml.walkforward import walk_forward


def test_walk_forward_never_tests_on_the_past() -> None:
    times = pd.date_range("2024-01-01", periods=1000, freq="h", tz="UTC")
    folds = walk_forward(times, train=500, val=100, test=100, step=100, embargo=1)
    assert len(folds) == 3  # 0-500 | 101 | 101 ... rolled by 100 until the data runs out
    for fold in folds:
        parts = [fold.train, fold.early_stop, fold.calibrate, fold.test]
        # Every part is strictly later than the one before, with a one-candle gap (embargo).
        for earlier, later in itertools.pairwise(parts):
            assert earlier.max() < later.min()
        assert fold.early_stop.min() - fold.train.max() == 2
        assert fold.test.min() - fold.calibrate.max() == 2
        assert len(fold.train) == 500 and len(fold.test) == 100
    assert folds[1].test.min() - folds[0].test.min() == 100


def test_pooled_coins_share_each_time_slot() -> None:
    one = pd.date_range("2024-01-01", periods=400, freq="D", tz="UTC")
    times = one.append(one).append(one)  # three coins, same days
    folds = walk_forward(times, train=200, val=40, test=40, step=40)
    for fold in folds:
        train_times, test_times = set(times[fold.train]), set(times[fold.test])
        assert max(train_times) < min(test_times)
        assert len(fold.test) == 3 * 40  # every coin's rows for those days


def test_classification_ignores_neutral_calls() -> None:
    p = np.array([0.7, 0.6, 0.5, 0.3, 0.2])
    y = np.array([1, 0, 1, 0, 1])
    result = metrics.classification(p, y)
    assert result["coverage"] == pytest.approx(0.8)
    assert result["accuracy"] == pytest.approx(0.5)  # 2 of the 4 Up/Down calls were right
    assert result["up_n"] == 2 and result["down_n"] == 2
    assert result["brier"] == pytest.approx(np.mean((p - y) ** 2))


def test_brier_of_a_coin_flip_is_a_quarter() -> None:
    y = np.array([0, 1, 1, 0])
    assert metrics.brier(np.full(4, 0.5), y) == pytest.approx(0.25)
    assert metrics.log_loss(np.full(4, 0.5), y) == pytest.approx(np.log(2))


def test_baselines() -> None:
    prev_up = np.array([1, 1, 0, 0])
    y = np.array([1, 0, 0, 1])
    result = metrics.baselines(prev_up, y, base_rate=0.5)
    assert result == {"naive": 0.5, "always_up": 0.5, "brier_base_rate": 0.25}


def test_strategy_pays_fees_on_every_trade() -> None:
    signal = np.array([1, 1, 0, 1])
    next_return = np.array([0.01, 0.02, -0.05, 0.0])
    result = metrics.simulate_long_only(signal, next_return, periods_per_year=8760)
    cost = 0.0015
    # buy, hold, sell (miss the -5%), buy again: three trades
    expected = (1 + 0.01 - cost) * (1 + 0.02) * (1 - cost) * (1 - cost) - 1
    assert result["trades"] == 3
    assert result["total_return"] == pytest.approx(expected)


def test_reliability_table_and_bootstrap() -> None:
    p = np.array([0.15, 0.18, 0.62, 0.64, 0.66])
    y = np.array([0, 0, 1, 1, 0])
    table = metrics.reliability_table(p, y)
    assert [row["bucket"] for row in table] == ["0.1-0.2", "0.6-0.7"]
    assert table[1]["share_up"] == pytest.approx(2 / 3)
    mean, low, high = metrics.bootstrap_ci(np.array([0.01, 0.02, 0.03, 0.02]))
    assert low <= mean <= high and low > 0
