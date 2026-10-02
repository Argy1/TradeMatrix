"""Feature and label tests, above all the no-leakage rules from docs/03."""

import numpy as np
import pandas as pd

from app.features.build import build_dataset, build_features, build_labels, feature_columns


def candles(n: int = 400, seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0, 0.004, n)) * close
    index = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + spread,
            "low": np.minimum(open_, close) - spread,
            "close": close,
            "volume": rng.uniform(10, 1000, n),
        },
        index=index,
    )


def test_changing_the_future_never_changes_past_features() -> None:
    data, btc = candles(), candles(seed=9)
    t = 300
    future_changed = data.copy()
    future_changed.iloc[t + 1 :] *= 1.5  # every candle AFTER t is different
    btc_changed = btc.copy()
    btc_changed.iloc[t + 1 :] *= 0.5

    before = build_features(data, btc).iloc[: t + 1]
    after = build_features(future_changed, btc_changed).iloc[: t + 1]
    pd.testing.assert_frame_equal(before, after)


def test_features_from_a_truncated_history_match_the_full_history() -> None:
    """What the live worker sees at time t (data up to t) equals what the backtest saw at t."""
    data = candles()
    full = build_features(data)
    for t in (120, 250, 399):
        live = build_features(data.iloc[: t + 1])
        pd.testing.assert_series_equal(live.iloc[-1], full.iloc[t], check_names=False)


def test_label_is_about_the_next_candle() -> None:
    data = candles(50)
    labels = build_labels(data)
    close = data["close"].to_numpy()
    for t in range(49):
        assert labels["label"].iloc[t] == float(close[t + 1] > close[t])
        assert np.isclose(labels["next_return"].iloc[t], close[t + 1] / close[t] - 1)
    assert np.isnan(labels["label"].iloc[-1])  # the next candle does not exist yet


def test_flat_next_close_counts_as_not_up() -> None:
    data = candles(5)
    data.iloc[3, data.columns.get_loc("close")] = data["close"].iloc[2]
    assert build_labels(data)["label"].iloc[2] == 0.0  # same as the outcome rule in docs/04


def test_dataset_drops_warm_up_and_the_unlabelled_last_row() -> None:
    data = candles()
    dataset = build_dataset(data)
    assert not dataset.isna().any().any()
    assert dataset.index[-1] == data.index[-2]
    assert 40 <= (dataset.index[0] - data.index[0]) / pd.Timedelta(hours=1) <= 80
    columns = feature_columns(dataset)
    assert "label" not in columns and "next_return" not in columns
    assert {"rsi14", "dist_ema50", "atr_pct", "hour_sin", "stoch_k"} <= set(columns)


def test_context_features_only_for_other_coins() -> None:
    assert "btc_ret_1" not in build_features(candles())
    assert "btc_ret_1" in build_features(candles(), candles(seed=5))
