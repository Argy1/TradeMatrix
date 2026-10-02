"""Turn closed candles into model features and labels (docs/03).

Rules that keep the backtest honest:
- Every feature at row t uses only candles 0..t, all of them already closed at t.
- The label at row t is about the NEXT candle: 1 if close[t+1] > close[t], else 0.
- Nothing is fitted or scaled here, so there is nothing that could peek at test data.
tests/test_features.py checks the first two rules directly.
"""

import numpy as np
import pandas as pd

from app.features import indicators as ind

RETURN_WINDOWS = (1, 3, 6, 12, 24)
CONTEXT_COLUMNS = ("btc_ret_1", "btc_ret_6", "btc_rsi14")


def build_features(candles: pd.DataFrame, btc: pd.DataFrame | None = None) -> pd.DataFrame:
    """Features for one asset and timeframe.

    `candles`: columns open, high, low, close, volume, indexed by open time (UTC), oldest
    first. `btc`: the same for Bitcoin, used as market context for the other coins.
    """
    o, h, low, c, v = (
        candles[col].astype("float64") for col in ("open", "high", "low", "close", "volume")
    )
    f = pd.DataFrame(index=candles.index)

    # Returns: how much the price moved over the last N candles.
    for n in RETURN_WINDOWS:
        f[f"ret_{n}"] = c.pct_change(n)
    f["log_ret_1"] = np.log(c / c.shift(1))

    # Trend: distance of the close from each EMA, in percent, plus crossovers.
    ema9, ema21, ema50 = ind.ema(c, 9), ind.ema(c, 21), ind.ema(c, 50)
    for name, line in (("ema9", ema9), ("ema21", ema21), ("ema50", ema50)):
        f[f"dist_{name}"] = (c / line - 1) * 100
    above = (ema9 > ema21).astype("float64").where(ema21.notna())
    f["ema9_gt_ema21"] = above
    # +1 if EMA 9 crossed above EMA 21 in the last 3 candles, -1 if it crossed below, else 0.
    crossed = above.diff()
    f["ema_cross_3"] = crossed.rolling(3, min_periods=1).sum().clip(-1, 1).where(above.notna())
    f["adx14"] = ind.adx(h, low, c)["adx"]

    # Momentum. MACD is divided by the price so BTC and XRP produce comparable numbers.
    f["rsi14"] = ind.rsi(c, 14)
    macd = ind.macd(c)
    f["macd_pct"] = macd["macd"] / c * 100
    f["macd_signal_pct"] = macd["signal"] / c * 100
    f["macd_hist_pct"] = macd["hist"] / c * 100
    f["stoch_k"] = ind.stochastic_k(h, low, c)

    # Volatility.
    bands = ind.bollinger(c)
    f["bb_percent_b"] = bands["percent_b"]
    f["bb_bandwidth"] = bands["bandwidth"]
    f["atr_pct"] = ind.atr(h, low, c) / c * 100
    f["ret_std_20"] = f["ret_1"].rolling(20, min_periods=20).std()

    # Volume: today's volume against its average, and the 10-candle OBV slope.
    f["vol_ratio_20"] = v / ind.sma(v, 20)
    obv = ind.obv(c, v)
    f["obv_slope_10"] = (obv - obv.shift(10)) / v.rolling(10, min_periods=10).sum()

    # Candle shape, as shares of the candle's full range (0 when the range is zero).
    rng = (h - low).replace(0, np.nan)
    f["body_pct"] = ((c - o).abs() / rng).fillna(0)
    f["upper_wick_pct"] = ((h - np.maximum(o, c)) / rng).fillna(0)
    f["lower_wick_pct"] = ((np.minimum(o, c) - low) / rng).fillna(0)

    # Calendar, as points on a circle so 23:00 and 00:00 end up close together.
    hours = candles.index.hour + candles.index.minute / 60
    f["hour_sin"] = np.sin(2 * np.pi * hours / 24)
    f["hour_cos"] = np.cos(2 * np.pi * hours / 24)
    f["dow_sin"] = np.sin(2 * np.pi * candles.index.dayofweek / 7)
    f["dow_cos"] = np.cos(2 * np.pi * candles.index.dayofweek / 7)

    if btc is not None:
        # Bitcoin often leads the market. Its candle at the same open time is closed too.
        btc_close = btc["close"].astype("float64").reindex(candles.index)
        f["btc_ret_1"] = btc_close.pct_change(1)
        f["btc_ret_6"] = btc_close.pct_change(6)
        f["btc_rsi14"] = ind.rsi(btc_close, 14)
    return f


def build_labels(candles: pd.DataFrame) -> pd.DataFrame:
    """label[t] = 1 if the next candle closes higher than candle t; next_return for the backtest.

    The last row has no next candle yet, so its label is NaN and it is never used for training.
    """
    c = candles["close"].astype("float64")
    next_close = c.shift(-1)
    label = (next_close > c).astype("float64").where(next_close.notna())
    return pd.DataFrame({"label": label, "next_return": next_close / c - 1}, index=candles.index)


def build_dataset(candles: pd.DataFrame, btc: pd.DataFrame | None = None) -> pd.DataFrame:
    """Features + labels, without the warm-up rows (where some indicator is still undefined)
    and without the last row (its label is unknown)."""
    features = build_features(candles, btc)
    data = features.join(build_labels(candles))
    data["prev_up"] = (candles["close"].astype("float64").diff() > 0).astype("float64")
    return data.dropna()


def feature_columns(data: pd.DataFrame) -> list[str]:
    return [col for col in data.columns if col not in ("label", "next_return", "prev_up")]
