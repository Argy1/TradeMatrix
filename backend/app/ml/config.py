"""Prediction settings in one place (docs/03). Tune them on validation data, never on test folds."""

from dataclasses import dataclass
from datetime import UTC, datetime

# A p_up between these two values is shown as Neutral ("too close to call").
NEUTRAL_LOW = 0.45
NEUTRAL_HIGH = 0.55

# Costs for the simulated strategy: 0.1% exchange fee and 0.05% slippage per trade side.
FEE = 0.001
SLIPPAGE = 0.0005

# Walk-forward windows in candles: train, validate (first half early stopping, second half
# calibration), test, and how far each fold moves forward. 4h uses a longer train window so
# it has at least ~2,000 rows; 1d pools all coins into one model for the same reason.
WINDOWS: dict[str, dict[str, int]] = {
    "1h": {"train": 4380, "val": 720, "test": 720, "step": 720},  # 6 months / 1 / 1 / 1
    "4h": {"train": 2190, "val": 180, "test": 180, "step": 180},  # 12 months / 1 / 1 / 1
    "1d": {"train": 730, "val": 90, "test": 90, "step": 90},  # 2 years / 3 / 3 / 3 months
}
EMBARGO = 1  # candles skipped between train, validation and test so labels never overlap

PERIODS_PER_YEAR = {"1h": 24 * 365, "4h": 6 * 365, "1d": 365}

# Deliberately small and heavily regularized: the signal in price data is weak.
XGB_PARAMS: dict = {
    "n_estimators": 600,
    "max_depth": 3,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 10,
    "reg_lambda": 5.0,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "early_stopping_rounds": 50,
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": 4,
}


# ---------- Tuning protocol (improvement round, 2026-10-03) ----------
# Candidates are compared ONLY on test folds inside the development window
# [DEV_FROM, DEV_UNTIL). The chosen candidate is then evaluated once on folds that start on or
# after EVAL_FROM. That keeps the final numbers free of tuning.
DEV_FROM = {
    "1h": datetime(2021, 7, 1, tzinfo=UTC),
    "4h": datetime(2022, 1, 1, tzinfo=UTC),
    "1d": datetime(2023, 4, 1, tzinfo=UTC),
}
DEV_UNTIL = datetime(2024, 10, 1, tzinfo=UTC)
EVAL_FROM = DEV_UNTIL


@dataclass(frozen=True)
class ModelConfig:
    name: str
    windows: dict[str, int]
    params: dict
    expanding: bool = False  # True: train on ALL earlier candles, not only the last window


# Bigger validation windows: more rows for early stopping and for calibration
# (the first run calibrated on as few as 45-90 candles, which made 4h and 1d overconfident).
BIG_VAL: dict[str, dict[str, int]] = {
    "1h": {"train": 4380, "val": 2160, "test": 720, "step": 720},  # 6 months / 3 / 1 / 1
    "4h": {"train": 2190, "val": 540, "test": 180, "step": 180},  # 12 months / 3 / 1 / 1
    "1d": {"train": 730, "val": 180, "test": 90, "step": 90},  # 2 years / 6 / 3 / 3 months
}

# Even simpler trees: shallower, more data per leaf, slower learning.
STRONG_REG: dict = XGB_PARAMS | {
    "max_depth": 2,
    "min_child_weight": 50,
    "learning_rate": 0.03,
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "n_estimators": 800,
    "early_stopping_rounds": 100,
}


def candidates(timeframe: str) -> list[ModelConfig]:
    """A deliberately short list: every extra candidate adds a chance of picking a lucky one."""
    return [
        ModelConfig("v1", WINDOWS[timeframe], XGB_PARAMS),
        ModelConfig("bigval", BIG_VAL[timeframe], XGB_PARAMS),
        ModelConfig("bigval_strongreg", BIG_VAL[timeframe], STRONG_REG),
        ModelConfig("expanding_strongreg", BIG_VAL[timeframe], STRONG_REG, expanding=True),
    ]


# The candidate used for the final evaluation and for live predictions, per timeframe.
# Set from reports/tuning_*.md (development window only).
# 2026-10-03, reports/tuning_2026-10-02.md: highest development-window Brier gain per timeframe
# (4h tie with bigval_strongreg broken by the accuracy edge; 1d has only 5 folds, keep v1).
CHOSEN: dict[str, str] = {"1h": "expanding_strongreg", "4h": "expanding_strongreg", "1d": "v1"}


def chosen(timeframe: str) -> ModelConfig:
    return next(c for c in candidates(timeframe) if c.name == CHOSEN[timeframe])
