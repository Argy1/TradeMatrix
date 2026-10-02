"""Train one XGBoost model and calibrate its probabilities."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from app.ml.config import XGB_PARAMS


def _logit(p: np.ndarray) -> np.ndarray:
    q = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(q / (1 - q))


@dataclass
class CalibratedModel:
    """XGBoost scores passed through Platt scaling: p = sigmoid(slope * logit(score) + intercept).

    Calibration makes "0.60" mean "Up about 60% of the time". The slope is never negative,
    so a higher model score can never turn into a lower probability (it stays monotonic).
    """

    booster: XGBClassifier
    features: list[str]
    slope: float
    intercept: float

    def raw(self, frame: pd.DataFrame) -> np.ndarray:
        return self.booster.predict_proba(frame[self.features])[:, 1]

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        z = self.slope * _logit(self.raw(frame)) + self.intercept
        return 1 / (1 + np.exp(-z))

    def importances(self) -> dict[str, float]:
        """Average gain per feature: how much each feature helped the trees (used for "why")."""
        gains = self.booster.get_booster().get_score(importance_type="gain")
        return {name: float(gains.get(name, 0.0)) for name in self.features}


def fit_calibrated(
    train: pd.DataFrame,
    early_stop: pd.DataFrame,
    calibrate: pd.DataFrame,
    features: list[str],
    params: dict | None = None,
) -> CalibratedModel:
    """Fit on `train`, stop adding trees when `early_stop` stops improving, then calibrate on
    `calibrate`. All three slices are in time order and never overlap."""
    booster = XGBClassifier(**(params or XGB_PARAMS))
    booster.fit(
        train[features],
        train["label"],
        eval_set=[(early_stop[features], early_stop["label"])],
        verbose=False,
    )
    model = CalibratedModel(booster, features, slope=1.0, intercept=0.0)

    y = calibrate["label"].to_numpy()
    scores = _logit(model.raw(calibrate)).reshape(-1, 1)
    if len(np.unique(y)) < 2:
        return model
    platt = LogisticRegression().fit(scores, y)
    slope, intercept = float(platt.coef_[0][0]), float(platt.intercept_[0])
    if slope <= 0:
        # On recent data a higher score did not mean "more likely Up": the honest answer is
        # the plain base rate for every row (and that shows up as no edge in the report).
        slope, intercept = 0.0, float(_logit(np.array([y.mean()]))[0])
    model.slope, model.intercept = slope, intercept
    return model
