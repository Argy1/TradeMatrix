"""Indicator tests: hand-computed values, slow loop references, and a no-look-ahead check.

The loop references below are written the "textbook" way on purpose. They are slow but easy
to verify by eye, so if the fast pandas version in app/features/indicators.py agrees with
them, we can trust it.
"""

import numpy as np
import pandas as pd
import pytest

from app.features import indicators as ind

# Closing prices of the widely used RSI teaching example (StockCharts "RSI" article).
RSI_CLOSES = [
    44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89,
    46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64, 46.21, 46.25,
    45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66, 43.13,
]  # fmt: skip


def random_candles(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """A random walk that looks like price data (deterministic thanks to the seed)."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0, 0.004, n)) * close
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + spread,
            "low": np.minimum(open_, close) - spread,
            "close": close,
            "volume": rng.uniform(10, 1000, n),
        }
    )


def wilder_loop(values: list[float], period: int) -> list[float]:
    """Wilder smoothing, textbook version: seed with a plain average, then roll forward."""
    out = [float("nan")] * len(values)
    if len(values) < period:
        return out
    average = sum(values[:period]) / period
    out[period - 1] = average
    for i in range(period, len(values)):
        average = (average * (period - 1) + values[i]) / period
        out[i] = average
    return out


def rsi_loop(closes: list[float], period: int = 14) -> list[float]:
    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = wilder_loop([max(c, 0.0) for c in changes], period)
    losses = wilder_loop([max(-c, 0.0) for c in changes], period)
    out = [float("nan")]  # the first close has no change
    for gain, loss in zip(gains, losses, strict=True):
        if np.isnan(gain):
            out.append(float("nan"))
        elif loss == 0:
            out.append(100.0)
        else:
            out.append(100 - 100 / (1 + gain / loss))
    return out


# ---------- moving averages ----------


def test_sma_and_ema_by_hand() -> None:
    series = pd.Series([1.0, 2, 3, 4, 5, 6])
    assert ind.sma(series, 3).tolist()[2:] == [2.0, 3.0, 4.0, 5.0]
    # EMA(3): seed = average(1, 2, 3) = 2, alpha = 0.5, so 0.5*4 + 0.5*2 = 3, then 4, then 5.
    result = ind.ema(series, 3)
    assert result.iloc[:2].isna().all()
    assert result.iloc[2:].tolist() == [2.0, 3.0, 4.0, 5.0]


def test_ema_is_nan_when_there_is_not_enough_history() -> None:
    assert ind.ema(pd.Series([1.0, 2.0]), 5).isna().all()


# ---------- RSI ----------


def test_rsi_matches_the_textbook_loop() -> None:
    closes = random_candles()["close"]
    expected = rsi_loop(closes.tolist())
    np.testing.assert_allclose(ind.rsi(closes).to_numpy(), expected, rtol=1e-10, equal_nan=True)


def test_rsi_teaching_example() -> None:
    result = ind.rsi(pd.Series(RSI_CLOSES))
    assert result.iloc[:14].isna().all()  # needs 14 price changes first
    # Published values for this dataset (they were computed from unrounded prices, so we
    # allow a small difference).
    assert result.iloc[14] == pytest.approx(70.5, abs=0.2)
    assert result.iloc[15] == pytest.approx(66.3, abs=0.2)
    assert result.iloc[19] == pytest.approx(58.0, abs=0.2)
    assert result.iloc[32] == pytest.approx(37.8, abs=0.2)


def test_rsi_extremes() -> None:
    rising = pd.Series(np.arange(1.0, 40.0))
    assert (ind.rsi(rising).dropna() == 100.0).all()
    falling = pd.Series(np.arange(40.0, 1.0, -1))
    assert ind.rsi(falling).dropna().max() == pytest.approx(0.0)
    values = ind.rsi(random_candles()["close"]).dropna()
    assert values.between(0, 100).all()


# ---------- MACD ----------


def test_macd_parts_are_consistent() -> None:
    close = random_candles()["close"]
    result = ind.macd(close)
    np.testing.assert_allclose(
        result["macd"].to_numpy(),
        (ind.ema(close, 12) - ind.ema(close, 26)).to_numpy(),
        equal_nan=True,
    )
    filled = result.dropna()
    np.testing.assert_allclose(filled["hist"], filled["macd"] - filled["signal"])
    # MACD needs 26 candles, and the signal line needs 9 MACD values after that.
    assert result["macd"].first_valid_index() == 25
    assert result["signal"].first_valid_index() == 33


def test_macd_is_zero_for_a_flat_price() -> None:
    result = ind.macd(pd.Series([50.0] * 60)).dropna()
    assert (result.abs() < 1e-12).all().all()


# ---------- Bollinger Bands ----------


def test_bollinger_by_hand() -> None:
    # Window (2, 4, 4, 4, 5, 5, 7, 9): mean 5, population standard deviation exactly 2.
    result = ind.bollinger(pd.Series([2.0, 4, 4, 4, 5, 5, 7, 9]), period=8, num_std=2)
    last = result.iloc[-1]
    assert last["mid"] == pytest.approx(5.0)
    assert last["upper"] == pytest.approx(9.0)
    assert last["lower"] == pytest.approx(1.0)
    assert last["percent_b"] == pytest.approx(1.0)  # the close (9) sits on the upper band
    assert last["bandwidth"] == pytest.approx(8.0 / 5.0)


def test_bollinger_flat_price_has_zero_width_and_no_percent_b() -> None:
    result = ind.bollinger(pd.Series([10.0] * 30)).iloc[-1]
    assert result["upper"] == result["lower"] == 10.0
    assert np.isnan(result["percent_b"])


# ---------- ATR / ADX ----------


def test_true_range_and_atr_by_hand() -> None:
    high = pd.Series([10.0, 12.0, 11.0, 15.0])
    low = pd.Series([8.0, 9.0, 10.0, 11.0])
    close = pd.Series([9.0, 11.0, 10.5, 14.0])
    # Row 0: 10-8 = 2. Row 1: max(3, |12-9|, |9-9|) = 3.
    # Row 2: max(1, 0, |10-11|) = 1. Row 3: max(4, |15-10.5|, 0.5) = 4.5.
    assert ind.true_range(high, low, close).tolist() == [2.0, 3.0, 1.0, 4.5]
    # ATR(2): seed = (2+3)/2 = 2.5, then (2.5 + 1)/2 = 1.75, then (1.75 + 4.5)/2 = 3.125.
    result = ind.atr(high, low, close, period=2)
    assert np.isnan(result.iloc[0])
    assert result.iloc[1:].tolist() == [2.5, 1.75, 3.125]


def test_atr_matches_the_textbook_loop() -> None:
    data = random_candles()
    true_range = ind.true_range(data["high"], data["low"], data["close"])
    expected = wilder_loop(true_range.tolist(), 14)
    result = ind.atr(data["high"], data["low"], data["close"])
    np.testing.assert_allclose(result.to_numpy(), expected, rtol=1e-10, equal_nan=True)


def test_adx_is_high_in_a_steady_trend_and_bounded() -> None:
    steps = np.arange(100.0)
    trend = ind.adx(pd.Series(steps + 2), pd.Series(steps), pd.Series(steps + 1)).dropna()
    assert trend["adx"].iloc[-1] > 90  # every candle moves up: a perfect trend
    assert (trend["plus_di"] > trend["minus_di"]).all()

    data = random_candles()
    result = ind.adx(data["high"], data["low"], data["close"])
    assert result["adx"].first_valid_index() == 27  # 14 for DI, then 14 more for ADX
    assert result.dropna().stack().between(0, 100).all()


# ---------- OBV ----------


def test_obv_by_hand() -> None:
    close = pd.Series([10.0, 11.0, 10.5, 10.5, 12.0])
    volume = pd.Series([100.0, 200.0, 300.0, 400.0, 500.0])
    # up: +200, down: -300, flat: 0, up: +500
    assert ind.obv(close, volume).tolist() == [0.0, 200.0, -100.0, -100.0, 400.0]


# ---------- no look-ahead (data leakage) ----------


def test_indicators_never_use_future_candles() -> None:
    """Changing candles after row t must not change any indicator value at or before t."""
    data = random_candles(300)
    cut = 200
    changed = data.copy()
    changed.loc[cut:, ["open", "high", "low", "close"]] *= 3.0
    changed.loc[cut:, "volume"] *= 5.0

    def all_indicators(frame: pd.DataFrame) -> pd.DataFrame:
        high, low, close, volume = frame["high"], frame["low"], frame["close"], frame["volume"]
        return pd.concat(
            [
                ind.sma(close, 20).rename("sma20"),
                ind.ema(close, 9).rename("ema9"),
                ind.ema(close, 50).rename("ema50"),
                ind.rsi(close).rename("rsi"),
                ind.macd(close),
                ind.bollinger(close),
                ind.atr(high, low, close).rename("atr"),
                ind.adx(high, low, close),
                ind.obv(close, volume).rename("obv"),
            ],
            axis=1,
        )

    before = all_indicators(data).iloc[:cut]
    after = all_indicators(changed).iloc[:cut]
    pd.testing.assert_frame_equal(before, after)
