"""Technical indicators, implemented with pandas so every step can be read and tested.

Conventions (the same ones TradingView and Wilder's book use, so the numbers match the
charts users compare us with):
- EMA and Wilder smoothing start from a simple average of the first `period` values.
- Bollinger Bands use the population standard deviation (ddof=0).
- The first rows, where an indicator does not have enough history yet, are NaN ("warm-up").

No look-ahead: the value at row t depends only on rows 0..t. tests/test_indicators.py
proves this by changing future rows and checking that earlier values stay the same.
"""

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple moving average."""
    return series.astype("float64").rolling(period, min_periods=period).mean()


def _seeded_ewm(series: pd.Series, period: int, alpha: float) -> pd.Series:
    """Exponential smoothing whose first value is the simple average of the first `period` values.

    next = alpha * value + (1 - alpha) * previous
    """
    values = series.astype("float64")
    seed = values.rolling(period, min_periods=period).mean()
    has_seed = seed.notna().to_numpy()
    if not has_seed.any():
        return pd.Series(np.nan, index=series.index, dtype="float64")
    first = int(has_seed.argmax())
    seeded = values.copy()
    seeded.iloc[:first] = np.nan
    seeded.iloc[first] = seed.iloc[first]
    # adjust=False gives exactly the recursive formula above, starting at the seed.
    return seeded.ewm(alpha=alpha, adjust=False).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential moving average: recent candles weigh more (alpha = 2 / (period + 1))."""
    return _seeded_ewm(series, period, 2.0 / (period + 1))


def wilder(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing (alpha = 1 / period), used by RSI, ATR and ADX."""
    return _seeded_ewm(series, period, 1.0 / period)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index, 0-100: average gain compared with average loss."""
    delta = close.astype("float64").diff()
    avg_gain = wilder(delta.clip(lower=0), period)
    avg_loss = wilder(-delta.clip(upper=0), period)
    value = 100 - 100 / (1 + avg_gain / avg_loss)
    value = value.where(avg_loss != 0, 100.0)  # no losses in the window means RSI 100
    return value.where(avg_gain.notna())  # keep the warm-up rows as NaN


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """MACD line (fast EMA - slow EMA), its signal line (EMA of MACD) and the histogram."""
    line = ema(close, fast) - ema(close, slow)
    signal_line = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": signal_line, "hist": line - signal_line})


def bollinger(close: pd.Series, period: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Bollinger Bands: a moving average with bands `num_std` standard deviations away."""
    values = close.astype("float64")
    mid = values.rolling(period, min_periods=period).mean()
    std = values.rolling(period, min_periods=period).std(ddof=0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    width = upper - lower
    # %B: 0 = at the lower band, 1 = at the upper band. Undefined when the bands touch.
    percent_b = ((values - lower) / width).where(width != 0)
    return pd.DataFrame(
        {
            "mid": mid,
            "upper": upper,
            "lower": lower,
            "percent_b": percent_b,
            "bandwidth": width / mid,
        }
    )


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Largest of: high-low, |high - previous close|, |low - previous close|."""
    high, low = high.astype("float64"), low.astype("float64")
    previous_close = close.astype("float64").shift(1)
    ranges = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    )
    return ranges.max(axis=1)  # the first row has no previous close, so it is high - low


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range: the typical candle size, a volatility measure."""
    return wilder(true_range(high, low, close), period)


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    """Average Directional Index: trend strength 0-100 (direction comes from +DI vs -DI)."""
    high, low = high.astype("float64"), low.astype("float64")
    up = high.diff()
    down = -low.diff()
    # Directional movement: only the larger of the two moves counts, and only if positive.
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=high.index)
    plus_dm[up.isna()] = np.nan
    minus_dm[up.isna()] = np.nan

    smoothed_tr = wilder(true_range(high, low, close), period)
    plus_di = 100 * wilder(plus_dm, period) / smoothed_tr
    minus_di = 100 * wilder(minus_dm, period) / smoothed_tr
    total = plus_di + minus_di
    dx = 100 * (plus_di - minus_di).abs() / total.where(total != 0, 1.0)
    return pd.DataFrame({"adx": wilder(dx, period), "plus_di": plus_di, "minus_di": minus_di})


def stochastic_k(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Stochastic %K, 0-100: where the close sits inside the last `period` candles' range."""
    lowest = low.astype("float64").rolling(period, min_periods=period).min()
    highest = high.astype("float64").rolling(period, min_periods=period).max()
    width = highest - lowest
    return (100 * (close.astype("float64") - lowest) / width).where(width != 0)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume: add volume on up candles, subtract it on down candles."""
    direction = np.sign(close.astype("float64").diff()).fillna(0.0)
    return (direction * volume.astype("float64")).cumsum()
