"""Prediction settings in one place (docs/03). Tune them on validation data, never on test folds."""

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
