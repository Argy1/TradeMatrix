"""How good are the probabilities? Every number here is reported next to a baseline."""

import itertools

import numpy as np

from app.ml.config import FEE, NEUTRAL_HIGH, NEUTRAL_LOW, SLIPPAGE

EPS = 1e-6


def signals(p: np.ndarray, low: float = NEUTRAL_LOW, high: float = NEUTRAL_HIGH) -> np.ndarray:
    """+1 = Up, -1 = Down, 0 = Neutral."""
    return np.where(p > high, 1, np.where(p < low, -1, 0))


def brier(p: np.ndarray, y: np.ndarray) -> float:
    """Mean squared error of the probability. 0.25 is a coin flip; lower is better."""
    return float(np.mean((p - y) ** 2))


def log_loss(p: np.ndarray, y: np.ndarray) -> float:
    q = np.clip(p, EPS, 1 - EPS)
    return float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))


def classification(p: np.ndarray, y: np.ndarray) -> dict:
    """Accuracy counts only Up/Down calls (Neutral is "no call"); coverage is the share of calls."""
    s = signals(p)
    called = s != 0
    actual = np.where(y == 1, 1, -1)
    out: dict = {
        "n": len(y),
        "coverage": float(called.mean()) if len(y) else 0.0,
        "accuracy": float((s[called] == actual[called]).mean()) if called.any() else None,
        "brier": brier(p, y),
        "log_loss": log_loss(p, y),
    }
    for name, side in (("up", 1), ("down", -1)):
        predicted, real = s == side, actual == side
        out[f"{name}_n"] = int(predicted.sum())
        out[f"{name}_precision"] = float((real[predicted]).mean()) if predicted.any() else None
        out[f"{name}_recall"] = float((predicted[real]).mean()) if real.any() else None
    return out


def baselines(prev_up: np.ndarray, y: np.ndarray, base_rate: float) -> dict:
    """The simple rules the model has to beat.

    naive: repeat the last candle's direction. always_up: always say Up.
    brier_base_rate: Brier score of always answering the training base rate (no peeking).
    """
    return {
        "naive": float((prev_up == y).mean()),
        "always_up": float(y.mean()),
        "brier_base_rate": brier(np.full(len(y), base_rate), y),
    }


def simulate_long_only(signal: np.ndarray, next_return: np.ndarray, periods_per_year: int) -> dict:
    """Hold the coin while the signal says Up, otherwise hold cash. Fees and slippage on every
    buy and sell. Long-only because a retail spot trader usually cannot short."""
    position = (signal == 1).astype(float)
    trades = np.abs(np.diff(np.concatenate([[0.0], position])))
    returns = position * next_return - trades * (FEE + SLIPPAGE)
    return _equity_stats(returns, periods_per_year) | {"trades": int(trades.sum())}


def buy_and_hold(next_return: np.ndarray, periods_per_year: int) -> dict:
    returns = next_return.astype(float).copy()
    if len(returns):
        returns[0] -= FEE + SLIPPAGE  # one buy at the start
    return _equity_stats(returns, periods_per_year) | {"trades": 1}


def _equity_stats(returns: np.ndarray, periods_per_year: int) -> dict:
    if len(returns) == 0:
        return {"total_return": 0.0, "max_drawdown": 0.0, "sharpe": None}
    equity = np.cumprod(1 + returns)
    drawdown = equity / np.maximum.accumulate(equity) - 1
    std = returns.std()
    sharpe = float(returns.mean() / std * np.sqrt(periods_per_year)) if std > 0 else None
    return {
        "total_return": float(equity[-1] - 1),
        "max_drawdown": float(drawdown.min()),
        "sharpe": sharpe,
    }


def reliability_table(p: np.ndarray, y: np.ndarray, bins: int = 10) -> list[dict]:
    """Calibration check: in each probability bucket, how often did Up actually happen?"""
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    for lo, hi in itertools.pairwise(edges):
        inside = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if inside.any():
            rows.append(
                {
                    "bucket": f"{lo:.1f}-{hi:.1f}",
                    "n": int(inside.sum()),
                    "mean_p": float(p[inside].mean()),
                    "share_up": float(y[inside].mean()),
                }
            )
    return rows


def bootstrap_ci(
    values: np.ndarray, n_resamples: int = 5000, seed: int = 0
) -> tuple[float, float, float]:
    """Mean and 95% interval of per-fold values, by resampling the folds.

    If the whole interval is above zero, the edge is unlikely to be luck."""
    values = np.asarray(values, dtype=float)
    if len(values) == 0:  # e.g. the model never left the Neutral band
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(n_resamples, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
