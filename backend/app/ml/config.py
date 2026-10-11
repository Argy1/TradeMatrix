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

PERIODS_PER_YEAR = {
    "1m": 60 * 24 * 365,
    "3m": 20 * 24 * 365,
    "5m": 12 * 24 * 365,
    "15m": 4 * 24 * 365,
    "30m": 2 * 24 * 365,
    "1h": 24 * 365,
    "4h": 6 * 365,
    "1d": 365,
}

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
    # Fast sizes only (see build_features): neutral values in quiet stretches, the extra
    # order-flow and context features, and one model for all coins instead of one per coin.
    quiet_safe: bool = False
    extended: bool = False
    pooled: bool = False
    skip_flat: bool = False  # a flat next candle gives no label (see build_labels)

    @property
    def feature_options(self) -> dict[str, bool]:
        return {"quiet_safe": self.quiet_safe, "extended": self.extended}

    @property
    def dataset_options(self) -> dict[str, bool]:
        return self.feature_options | {"skip_flat": self.skip_flat}


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


# ---------- Fast sizes (Phase 5b, 2026-10-11) ----------
# Windows in candles. A week of 1m candles is already 10,080 rows, so the test folds are short
# in days and there are many of them. History per size: app/data/history.py.
FAST_WINDOWS: dict[str, dict[str, int]] = {
    "1m": {"train": 86_400, "val": 20_160, "test": 10_080, "step": 10_080},  # 60 d / 14 / 7 / 7
    "3m": {"train": 43_200, "val": 9_600, "test": 3_360, "step": 3_360},  # 90 d / 20 / 7 / 7
    "5m": {"train": 34_560, "val": 8_064, "test": 4_032, "step": 4_032},  # 120 d / 28 / 14 / 14
    "15m": {"train": 17_280, "val": 2_880, "test": 1_344, "step": 1_344},  # 180 d / 30 / 14 / 14
    "30m": {"train": 8_640, "val": 2_880, "test": 672, "step": 672},  # 180 d / 60 / 14 / 14
}
# Same protocol as above: candidates are compared on test folds before this date, and the
# chosen one is scored once on the folds from this date on.
FAST_EVAL_FROM = {
    "1m": datetime(2026, 7, 1, tzinfo=UTC),
    "3m": datetime(2026, 6, 1, tzinfo=UTC),
    "5m": datetime(2026, 4, 1, tzinfo=UTC),
    "15m": datetime(2026, 4, 1, tzinfo=UTC),
    "30m": datetime(2026, 4, 1, tzinfo=UTC),
}


def is_fast(timeframe: str) -> bool:
    return timeframe in FAST_WINDOWS


def dev_window(timeframe: str) -> tuple[datetime | None, datetime]:
    """(from, until) of the development window; None means "from the first fold"."""
    if is_fast(timeframe):
        return None, FAST_EVAL_FROM[timeframe]
    return DEV_FROM[timeframe], DEV_UNTIL


def eval_from(timeframe: str) -> datetime:
    return FAST_EVAL_FROM[timeframe] if is_fast(timeframe) else EVAL_FROM


def candidates(timeframe: str) -> list[ModelConfig]:
    """A deliberately short list: every extra candidate adds a chance of picking a lucky one."""
    if is_fast(timeframe):
        windows = FAST_WINDOWS[timeframe]
        fast = {"quiet_safe": True, "skip_flat": True}
        return [
            ModelConfig("fast_basic", windows, STRONG_REG, **fast),
            ModelConfig("fast_flow", windows, STRONG_REG, extended=True, **fast),
            ModelConfig(
                "fast_flow_pooled", windows, STRONG_REG, extended=True, pooled=True, **fast
            ),
        ]
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
