"""Fast candle sizes (Phase 5b): time maths, quiet-safe and extended features, the stricter
verdict, and the history files."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from app.data import history
from app.data.exchanges.base import Candle, ExchangeClient
from app.data.exchanges.binance import _parse
from app.features.build import build_dataset, build_features, feature_columns, labelled
from app.ml import metrics
from app.ml.backtest import fold_metrics, fold_rows_of, summarize, summarize_coins
from app.ml.config import FAST_WINDOWS, PERIODS_PER_YEAR, candidates, dev_window, eval_from, is_fast
from app.timeframes import (
    FAST_TIMEFRAMES,
    TIMEFRAMES,
    floor_time,
    is_aligned,
    last_closed_open_time,
)


# ---------------------------------------------------------------- time maths
def test_fast_sizes_are_known_and_10m_is_not() -> None:
    assert list(FAST_TIMEFRAMES) == ["1m", "3m", "5m", "15m", "30m"]
    assert "10m" not in TIMEFRAMES  # Binance has no 10m candle; 15m takes its place
    assert list(TIMEFRAMES) == ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d"]
    assert set(FAST_WINDOWS) == set(FAST_TIMEFRAMES) <= set(PERIODS_PER_YEAR)


def test_fast_candles_open_on_their_grid() -> None:
    moment = datetime(2026, 10, 11, 14, 37, 42, tzinfo=UTC)
    assert floor_time(moment, "1m") == datetime(2026, 10, 11, 14, 37, tzinfo=UTC)
    assert floor_time(moment, "3m") == datetime(2026, 10, 11, 14, 36, tzinfo=UTC)
    assert floor_time(moment, "5m") == datetime(2026, 10, 11, 14, 35, tzinfo=UTC)
    assert floor_time(moment, "15m") == datetime(2026, 10, 11, 14, 30, tzinfo=UTC)
    assert floor_time(moment, "30m") == datetime(2026, 10, 11, 14, 30, tzinfo=UTC)
    assert is_aligned(datetime(2026, 10, 11, 14, 45, tzinfo=UTC), "15m")
    assert not is_aligned(datetime(2026, 10, 11, 14, 40, tzinfo=UTC), "15m")
    # At 14:37:42 the newest CLOSED 5m candle is the one that opened at 14:30.
    assert last_closed_open_time(moment, "5m") == datetime(2026, 10, 11, 14, 30, tzinfo=UTC)


def test_settings_exist_for_every_fast_size() -> None:
    for timeframe in FAST_TIMEFRAMES:
        assert is_fast(timeframe)
        names = [c.name for c in candidates(timeframe)]
        assert names == ["fast_basic", "fast_flow", "fast_flow_pooled"]
        assert all(c.quiet_safe for c in candidates(timeframe))
        start, until = dev_window(timeframe)
        assert start is None and until == eval_from(timeframe)  # tuning never sees the test period
    assert not is_fast("1h")
    assert candidates("1h")[0].name == "v1"  # slow sizes keep their own list


# ---------------------------------------------------------------- features
def minute_candles(n: int = 1400, seed: int = 4) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.0005, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0, 0.0002, n)) * close
    volume = rng.uniform(1, 50, n)
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + spread,
            "low": np.minimum(open_, close) - spread,
            "close": close,
            "volume": volume,
            "trades": rng.integers(5, 400, n).astype(float),
            "taker_buy_volume": volume * rng.uniform(0.2, 0.8, n),
        },
        index=pd.date_range("2026-09-01", periods=n, freq="min", tz="UTC"),
    )


def test_extended_features_never_look_ahead() -> None:
    data, btc = minute_candles(), minute_candles(seed=8)
    t = 900
    changed, btc_changed = data.copy(), btc.copy()
    changed.iloc[t + 1 :] *= 1.3  # every candle AFTER t is different
    btc_changed.iloc[t + 1 :] *= 0.7
    options = {"quiet_safe": True, "extended": True}
    before = build_features(data, btc, **options).iloc[: t + 1]
    after = build_features(changed, btc_changed, **options).iloc[: t + 1]
    pd.testing.assert_frame_equal(before, after)
    assert {
        "taker_buy_share",
        "taker_share_20",
        "trades_ratio_20",
        "ret_288",
        "dist_ema200",
    } <= set(before.columns)


def test_live_window_of_1000_candles_gives_the_training_features() -> None:
    """The worker builds features from the newest 1,000 candles, training from the whole file.
    Both must give the same numbers, including the slow EMA 200."""
    data = minute_candles(n=3000)
    options = {"quiet_safe": True, "extended": True}
    full = build_features(data, **options).iloc[-1]
    live = build_features(data.iloc[-1000:], **options).iloc[-1]
    assert not live.isna().any()
    np.testing.assert_allclose(live.to_numpy(), full.to_numpy(), rtol=1e-3, atol=1e-6)


def test_a_quiet_stretch_keeps_its_features() -> None:
    """40 minutes without a trade: the price does not move and the volume is zero."""
    data = minute_candles()
    quiet = slice(1000, 1040)
    price = data["close"].iloc[999]
    for column in ("open", "high", "low", "close"):
        data.iloc[quiet, data.columns.get_loc(column)] = price
    for column in ("volume", "trades", "taker_buy_volume"):
        data.iloc[quiet, data.columns.get_loc(column)] = 0.0

    row = build_features(data, quiet_safe=True, extended=True).iloc[1039]
    assert not row.isna().any() and np.isfinite(row.to_numpy()).all()
    assert row["stoch_k"] == 50.0 and row["bb_percent_b"] == 0.5  # "in the middle"
    assert row["vol_ratio_20"] == 1.0 and row["obv_slope_10"] == 0.0
    assert row["taker_buy_share"] == 0.5 and row["trades_ratio_20"] == 1.0
    # Without the switch those rows are NaN and would be dropped: no signal in a calm minute.
    assert build_features(data).iloc[1039].isna().any()
    kept = build_dataset(data, quiet_safe=True, extended=True)
    assert data.index[1020] in kept.index


def test_the_switches_leave_the_slow_features_alone() -> None:
    data = minute_candles()
    plain = build_features(data)
    safe = build_features(data, quiet_safe=True)
    pd.testing.assert_frame_equal(plain, safe)  # no quiet stretch here, so nothing differs
    extended = build_features(data, quiet_safe=True, extended=True)
    pd.testing.assert_frame_equal(plain, extended[plain.columns])
    assert len(feature_columns(extended)) == len(feature_columns(plain)) + 8


# ---------------------------------------------------------------- flat candles and the verdict
def test_a_flat_next_candle_has_no_label_on_fast_sizes() -> None:
    data = minute_candles(400)
    data.iloc[301, data.columns.get_loc("close")] = data["close"].iloc[300]  # candle 301 is flat
    slow = build_dataset(data, quiet_safe=True, extended=True)
    fast = build_dataset(data, quiet_safe=True, extended=True, skip_flat=True)
    when = data.index[300]
    assert slow.loc[when, "label"] == 0.0  # 1h/4h/1d rule: flat counts as "not up"
    assert np.isnan(fast.loc[when, "label"])  # fast rule: no result
    assert fast.loc[when, "next_return"] == 0.0
    assert len(fast) == len(slow)  # the row stays: the model still predicts it
    assert len(labelled(fast)) == len(fast) - 1
    assert not fast.drop(columns="label").isna().any().any()
    assert all(c.skip_flat for tf in FAST_TIMEFRAMES for c in candidates(tf))
    assert not any(c.skip_flat for c in candidates("1h"))


def predictions(p_up, label, next_return, prev_up=None, fold=None, base_rate=0.5) -> pd.DataFrame:
    n = len(p_up)
    return pd.DataFrame(
        {
            "p_up": np.asarray(p_up, dtype=float),
            "label": np.asarray(label, dtype=float),
            "prev_up": np.zeros(n) if prev_up is None else np.asarray(prev_up, dtype=float),
            "next_return": np.asarray(next_return, dtype=float),
            "base_rate": base_rate,
            "fold": np.ones(n, dtype=int) if fold is None else fold,
        },
        index=pd.date_range("2026-08-01", periods=n, freq="min", tz="UTC"),
    )


def test_fold_metrics_score_every_simple_rule_and_skip_flat_rows() -> None:
    #            flat     up    down  up    up
    frame = predictions(
        p_up=[0.30, 0.70, 0.30, 0.50, 0.20],
        label=[np.nan, 1, 0, 1, 1],
        next_return=[0.0, 0.01, -0.01, 0.02, 0.01],
        prev_up=[0, 0, 1, 0, 1],
    )
    m = fold_metrics(frame)
    assert m["coverage"] == pytest.approx(0.8)  # 4 of the 5 signals were not Neutral
    assert m["accuracy"] == pytest.approx(2 / 3)  # the call on the flat candle is not counted
    assert m["flat_share"] == pytest.approx(0.2)
    assert m["always_up"] == pytest.approx(0.75) and m["always_down"] == pytest.approx(0.25)
    assert m["naive"] == pytest.approx(0.25)
    assert m["brier"] == pytest.approx(np.mean([0.09, 0.09, 0.25, 0.64]))


def quiet_market(seed: int, folds: int = 12, per_fold: int = 400) -> dict:
    """Half of the candles are flat (no result); the others go up or down like a coin flip."""
    rng = np.random.default_rng(seed)
    n = folds * per_fold
    flat = rng.random(n) < 0.5
    up = (rng.random(n) < 0.5) & ~flat
    return {
        "flat": flat,
        "up": up,
        "label": np.where(flat, np.nan, up.astype(float)),
        "next_return": np.where(flat, 0.0, np.where(up, 0.001, -0.001)),
        "prev_up": (rng.random(n) < 0.5).astype(float),
        "fold": np.repeat(np.arange(1, folds + 1), per_fold),
    }


def score(p_up, market, base_rate=0.5) -> dict:
    preds = predictions(
        p_up, market["label"], market["next_return"], market["prev_up"], market["fold"], base_rate
    )
    return summarize(preds, fold_rows_of(preds), "1m")


def test_saying_down_in_quiet_minutes_is_not_a_passing_model() -> None:
    """A "model" that only knows when the market is quiet and says Down there would be right
    100% of the time if flat counted as Down. With no result for flat candles it has nothing."""
    market = quiet_market(seed=1)
    summary = score(np.where(market["flat"], 0.2, 0.5), market)  # Down before flat, else Neutral
    assert summary["model"]["coverage"] == pytest.approx(0.5, abs=0.03)
    assert summary["model"]["accuracy"] is None  # no call had a result
    assert summary["model"]["flat_share"] == pytest.approx(0.5, abs=0.03)
    assert summary["beats_baselines"] is False


def test_a_model_that_knows_the_direction_passes() -> None:
    market = quiet_market(seed=2)
    right = np.random.default_rng(5).random(len(market["up"])) < 0.62
    says_up = np.where(right, market["up"], ~market["up"])
    summary = score(np.where(says_up, 0.62, 0.38), market)  # says 62% and is right 62%
    assert summary["model"]["accuracy"] == pytest.approx(0.62, abs=0.03)
    assert summary["beats_baselines"] is True


def test_a_coin_flip_does_not_pass() -> None:
    market = quiet_market(seed=2)
    says_up = np.random.default_rng(6).random(len(market["up"])) < 0.5
    summary = score(np.where(says_up, 0.62, 0.38), market)
    assert summary["model"]["accuracy"] == pytest.approx(0.5, abs=0.03)
    assert summary["beats_baselines"] is False


def test_always_down_and_reverse_are_baselines() -> None:
    result = metrics.baselines(np.array([1, 1, 0, 0]), np.array([0, 0, 0, 1]), base_rate=0.25)
    assert result["always_up"] == pytest.approx(0.25)
    assert result["always_down"] == pytest.approx(0.75)
    assert result["naive"] == pytest.approx(0.25) and result["reverse"] == pytest.approx(0.75)


def test_a_model_that_only_knows_the_bounce_does_not_pass() -> None:
    """The price bounces: after an up candle the next one is down 65% of the time. A model
    that predicts exactly that is right 65%, far above a coin flip, but the one-line rule
    "reverse the last candle" is right just as often. No edge, so no pass."""
    rng = np.random.default_rng(11)
    folds, per_fold = 12, 500
    n = folds * per_fold
    prev_up = rng.random(n) < 0.5
    bounced = rng.random(n) < 0.65
    up = np.where(bounced, ~prev_up, prev_up)
    preds = predictions(
        np.where(prev_up, 0.35, 0.65),  # always says "the opposite of the last candle"
        up.astype(float),
        np.where(up, 0.001, -0.001),
        prev_up.astype(float),
        np.repeat(np.arange(1, folds + 1), per_fold),
    )
    summary = summarize(preds, fold_rows_of(preds), "1m")
    assert summary["model"]["accuracy"] == pytest.approx(0.65, abs=0.02)
    assert summary["baselines"]["reverse"] == pytest.approx(0.65, abs=0.02)
    assert summary["accuracy_edge_vs_naive"][1] > 0.2  # looks huge against the old baseline
    assert abs(summary["accuracy_edge_vs_best"][0]) < 0.005  # and is nothing against the rule
    assert summary["beats_baselines"] is False


def test_a_model_must_beat_always_down_too() -> None:
    """In a falling market "always Down" is right 60% of the time. A model that is right 57%
    beats the naive rule but not that one, so it does not pass."""
    rng = np.random.default_rng(7)
    folds, per_fold = 12, 500
    n = folds * per_fold
    up = rng.random(n) < 0.40
    right = rng.random(n) < 0.57
    says_up = np.where(right, up, ~up)
    preds = predictions(
        np.where(says_up, 0.57, 0.43),
        up.astype(float),
        np.where(up, 0.001, -0.001),
        (rng.random(n) < 0.5).astype(float),
        np.repeat(np.arange(1, folds + 1), per_fold),
        base_rate=0.40,
    )
    summary = summarize(preds, fold_rows_of(preds), "1m")
    assert summary["accuracy_edge_vs_naive"][1] > 0
    assert summary["accuracy_edge_vs_best"][2] < 0
    assert summary["beats_baselines"] is False


def test_a_pooled_model_is_scored_coin_by_coin() -> None:
    good, bad = quiet_market(seed=3), quiet_market(seed=4)
    good_p = np.where(good["up"], 0.7, 0.3)  # always right when the candle moves
    bad_p = np.where(bad["up"], 0.3, 0.7)  # always wrong
    one = predictions(good_p, good["label"], good["next_return"], good["prev_up"], good["fold"])
    two = predictions(bad_p, bad["label"], bad["next_return"], bad["prev_up"], bad["fold"])
    pooled = pd.concat([one.assign(asset_id=1.0), two.assign(asset_id=2.0)]).sort_index(
        kind="stable"
    )
    scored = summarize_coins(pooled, "1m", {"AAA": 1, "BBB": 2, "CCC": 3})
    assert set(scored) == {"AAA", "BBB"}  # CCC has no rows
    assert scored["AAA"]["beats_baselines"] is True
    assert scored["BBB"]["beats_baselines"] is False


# ---------------------------------------------------------------- exchange rows and history files
def test_kline_rows_keep_trades_and_taker_volume() -> None:
    row = [1791730200000, "83158.13", "83160.00", "83150.00", "83158.12", "1.5", 1791730259999,
           "124737.2", 87, "0.9", "74842.3", "0"]  # fmt: skip
    candle = _parse(row)
    assert candle.trades == 87 and candle.taker_buy_volume == Decimal("0.9")
    assert _parse(row[:7]).trades is None  # short rows (other exchanges, old tests) still work


class FakeExchange(ExchangeClient):
    name = "fake"

    def __init__(self, candles: list[Candle]) -> None:
        self.candles = candles
        self.starts: list[datetime] = []

    async def get_klines(self, symbol, timeframe, start=None, end=None, limit=None):
        self.starts.append(start)
        return [c for c in self.candles if c.open_time >= start][:limit]

    async def get_last_price(self, symbol):
        return Decimal("0")


def minute(i: int) -> Candle:
    start = datetime(2026, 10, 11, 12, 0, tzinfo=UTC) + timedelta(minutes=i)
    return Candle(start, Decimal("100"), Decimal("101"), Decimal("99"), Decimal("100.5"),
                  Decimal("2"), trades=10 + i, taker_buy_volume=Decimal("1.2"))  # fmt: skip


async def test_history_download_resumes_and_never_duplicates(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    now = datetime(2026, 10, 11, 13, 0, tzinfo=UTC)
    exchange = FakeExchange([minute(i) for i in range(25)])

    # First run: three request series of 10, 10 and 5 candles.
    assert await history.update(exchange, "BTC", "BTCUSDT", "1m", now=now, chunk=10) == 25
    assert len(exchange.starts) == 3
    stored = history.load("BTC", "1m")
    assert len(stored) == 25 and stored.index.is_monotonic_increasing
    assert list(stored.columns) == history.COLUMNS
    assert stored["trades"].iloc[-1] == 34.0 and stored["taker_buy_volume"].iloc[0] == 1.2

    # Second run after 5 more candles: it continues right after the newest stored one.
    exchange.candles += [minute(i) for i in range(25, 30)]
    assert await history.update(exchange, "BTC", "BTCUSDT", "1m", now=now, chunk=10) == 5
    assert exchange.starts[-1] == minute(25).open_time
    assert len(history.load("BTC", "1m")) == 30

    # Nothing new: nothing added, nothing lost.
    assert await history.update(exchange, "BTC", "BTCUSDT", "1m", now=now, chunk=10) == 0
    assert history.load("BTC", "1m").index.is_unique


def test_missing_history_file_says_what_to_run(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match=r"app\.data\.history"):
        history.load("BTC", "1m")
