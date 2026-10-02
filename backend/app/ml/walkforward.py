"""Walk-forward splits: train on the past, test on the next period, then roll forward.

This copies how the model is used live: it is always trained on data older than what it
predicts. A random split would let the model "see the future" and look far better than it is.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Fold:
    number: int
    train: np.ndarray  # row positions
    early_stop: np.ndarray  # first half of validation: when to stop adding trees
    calibrate: np.ndarray  # second half of validation: fit the probability calibration
    test: np.ndarray


def walk_forward(
    times: pd.DatetimeIndex,
    *,
    train: int,
    val: int,
    test: int,
    step: int,
    embargo: int = 1,
    expanding: bool = False,
) -> list[Fold]:
    """Folds over candle times (sizes are counted in candles, not rows).

    `times` may repeat when several coins are pooled; all rows with the same time always land
    in the same part, so no coin's future can leak into another coin's past.
    With `expanding=True` each fold trains on ALL earlier candles instead of the last `train`.
    """
    unique = pd.DatetimeIndex(sorted(set(times)))
    position = unique.get_indexer(times)  # each row's candle number
    folds: list[Fold] = []
    start = 0
    while True:
        train_end = start + train
        val_start = train_end + embargo
        val_end = val_start + val
        test_start = val_end + embargo
        test_end = test_start + test
        if test_end > len(unique):
            break
        middle = val_start + val // 2

        def rows(lo: int, hi: int) -> np.ndarray:
            return np.flatnonzero((position >= lo) & (position < hi))

        folds.append(
            Fold(
                number=len(folds) + 1,
                train=rows(0 if expanding else start, train_end),
                early_stop=rows(val_start, middle),
                calibrate=rows(middle, val_end),
                test=rows(test_start, test_end),
            )
        )
        start += step
    return folds
