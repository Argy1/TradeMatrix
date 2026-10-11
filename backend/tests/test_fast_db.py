"""Fast sizes against the REAL database. Run on purpose with: uv run pytest -m db

Each test works inside a transaction that is rolled back (the `session` fixture in
conftest.py). Almost everything is dated in 2001, far from any real row, so real data is
never touched; the one test that needs "now" says so.
"""

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.exchanges.base import Candle
from app.features.build import build_dataset, feature_columns, labelled
from app.ml import stats
from app.ml.config import XGB_PARAMS
from app.ml.performance import Resolved, totals_of
from app.ml.predict import resolve_outcomes, run_predictions
from app.ml.registry import ModelBundle
from app.ml.train import fit_calibrated
from app.timeframes import TIMEFRAMES, last_closed_open_time

pytestmark = pytest.mark.db
T0 = datetime(2001, 1, 1, tzinfo=UTC)
MINUTE = timedelta(minutes=1)


@pytest.fixture(autouse=True)
async def needs_the_migration(session: AsyncSession) -> None:
    found = await session.execute(text("select to_regclass('public.signal_stats_daily')"))
    if found.scalar_one() is None:
        pytest.skip("migration 20261011230000_fast_timeframes is not applied yet")


def candle(open_time: datetime, close: str, trades: int = 12) -> Candle:
    return Candle(open_time, Decimal("100"), Decimal("110"), Decimal("90"), Decimal(close),
                  Decimal("3"), trades=trades, taker_buy_volume=Decimal("1.8"))  # fmt: skip


async def model_version(session: AsyncSession, asset_id: int, timeframe: str) -> int:
    """An inactive model version just for the test."""
    created = await session.execute(
        text(
            "insert into model_versions (asset_id, timeframe, train_start, train_end, "
            "artifact_path) values (:a, :tf, :t, :t, 'test/none.joblib') returning id"
        ),
        {"a": asset_id, "tf": timeframe, "t": T0},
    )
    return created.scalar_one()


async def signal(
    session: AsyncSession,
    asset_id: int,
    model_id: int,
    timeframe: str,
    base: datetime,
    label: str,
    p_up: float,
) -> int:
    created = await session.execute(
        text(
            "insert into predictions (asset_id, timeframe, base_open_time, target_open_time, "
            "base_close, p_ml, p_up, label, model_version_id, feature_values) "
            "values (:a, :tf, :base, :target, 100, :p, :p, :label, :m, cast(:v as real[])) "
            "returning id"
        ),
        {
            "a": asset_id,
            "tf": timeframe,
            "base": base,
            "target": base + TIMEFRAMES[timeframe],
            "p": p_up,
            "label": label,
            "m": model_id,
            "v": [1.0],
        },
    )
    return created.scalar_one()


async def test_every_size_is_accepted_and_10m_is_not(session: AsyncSession) -> None:
    btc = await repo.get_asset(session, "BTC")
    for timeframe in TIMEFRAMES:
        await repo.upsert_candles(session, btc.id, timeframe, [candle(T0, "101")])
    with pytest.raises(Exception, match="candles_timeframe_check"):
        async with session.begin_nested():
            await repo.upsert_candles(session, btc.id, "10m", [candle(T0, "101")])


async def test_fast_candles_keep_order_flow_and_come_back_in_one_read(
    session: AsyncSession,
) -> None:
    btc, eth = await repo.get_asset(session, "BTC"), await repo.get_asset(session, "ETH")
    await repo.upsert_candles(
        session,
        btc.id,
        "1m",
        [candle(T0 + i * MINUTE, f"10{i}.12345678", 10 + i) for i in range(5)],
    )
    await repo.upsert_candles(session, eth.id, "1m", [candle(T0, "95"), candle(T0 + MINUTE, "96")])

    latest = await repo.latest_open_times(session, ["1m", "3m"])
    # (after go-live the real newest candle is later than 2001; before it, these are the newest)
    assert latest[(btc.id, "1m")] >= T0 + 4 * MINUTE
    assert (eth.id, "3m") in latest

    # Old rows only: ask for the candles as they were at the end of the test day.
    frames = {}
    for asset in (btc, eth):
        rows = await session.execute(
            text(
                "select trades, taker_buy_volume, close from candles where asset_id = :a "
                "and timeframe = '1m' and open_time < :end order by open_time"
            ),
            {"a": asset.id, "end": T0 + timedelta(days=1)},
        )
        frames[asset.symbol] = rows.all()
    assert [r[0] for r in frames["BTC"]] == [10, 11, 12, 13, 14]
    assert frames["BTC"][0][1] == Decimal("1.8") and frames["BTC"][4][2] == Decimal("104.12345678")
    assert len(frames["ETH"]) == 2


async def test_feature_frames_reads_many_coins_at_once(session: AsyncSession) -> None:
    """Uses a size and a time nobody else writes to: 30m candles in the year 2100."""
    far = datetime(2100, 1, 1, tzinfo=UTC)
    step = timedelta(minutes=30)
    btc, eth = await repo.get_asset(session, "BTC"), await repo.get_asset(session, "ETH")
    await repo.upsert_candles(
        session, btc.id, "30m", [candle(far + i * step, f"10{i}.5", 20 + i) for i in range(6)]
    )
    await repo.upsert_candles(
        session, eth.id, "30m", [candle(far + i * step, "95") for i in range(2)]
    )

    frames = await repo.feature_frames(session, [btc.id, eth.id], "30m", limit=4)
    own = frames[btc.id]
    assert list(own.frame.columns) == [
        "open", "high", "low", "close", "volume", "trades", "taker_buy_volume",
    ]  # fmt: skip
    assert list(own.frame.index) == [far + i * step for i in range(2, 6)]  # newest 4, oldest first
    assert own.frame["trades"].tolist() == [22.0, 23.0, 24.0, 25.0]
    assert own.frame["close"].iloc[-1] == 105.5 and own.last_close == Decimal("105.5")
    assert own.frame.dtypes.eq("float64").all()
    # (after go-live ETH also has real 30m candles; the two made-up ones are the newest)
    assert list(frames[eth.id].frame.index[-2:]) == [far, far + step]


async def test_a_flat_candle_has_no_result_on_fast_sizes_only(session: AsyncSession) -> None:
    btc = await repo.get_asset(session, "BTC")
    fast, slow = (
        await model_version(session, btc.id, "1m"),
        await model_version(session, btc.id, "1h"),
    )
    # 1m target candles after base candles that closed at 100: up, flat, down, flat.
    closes = ["101", "100", "99", "100"]
    await repo.upsert_candles(
        session, btc.id, "1m", [candle(T0 + (i + 1) * MINUTE, c) for i, c in enumerate(closes)]
    )
    labels = ["up", "down", "up", "neutral"]
    ids = [
        await signal(session, btc.id, fast, "1m", T0 + i * MINUTE, label, 0.6)
        for i, label in enumerate(labels)
    ]
    # One 1h signal whose target candle closes flat: the slow rule still calls that "down".
    await repo.upsert_candles(session, btc.id, "1h", [candle(T0 + timedelta(hours=1), "100")])
    slow_id = await signal(session, btc.id, slow, "1h", T0, "down", 0.4)

    now = T0 + timedelta(hours=3)
    first = await resolve_outcomes(session, ["1m", "1h"], now=now, look_back=timedelta(days=1))
    assert first == {"resolved": 5}
    again = await resolve_outcomes(session, ["1m", "1h"], now=now, look_back=timedelta(days=1))
    assert again == {"resolved": 0}  # idempotent

    rows = await session.execute(
        text(
            "select prediction_id, actual_direction, correct from prediction_outcomes "
            "where prediction_id = any(:ids)"
        ),
        {"ids": [*ids, slow_id]},
    )
    result = {r[0]: (r[1], r[2]) for r in rows}
    assert [result[i] for i in ids] == [
        ("up", True),  # said Up, closed higher
        ("flat", None),  # said Down, closed flat: no result on a fast size
        ("down", False),  # said Up, closed lower
        ("flat", None),  # Neutral and flat: no result either way
    ]
    assert result[slow_id] == ("down", True)  # 1h: flat counts as down, as before

    # Only what was asked for: a 1m signal is not resolved by a run for the slow sizes.
    late = await signal(session, btc.id, fast, "1m", T0 + 10 * MINUTE, "up", 0.6)
    await repo.upsert_candles(session, btc.id, "1m", [candle(T0 + 11 * MINUTE, "105")])
    assert await resolve_outcomes(session, ["1h"], now=now, look_back=timedelta(days=1)) == {
        "resolved": 0
    }
    assert late not in result


async def day_row(session: AsyncSession, asset_id: int, timeframe: str) -> dict:
    row = await session.execute(
        text(
            "select * from signal_stats_daily where asset_id = :a and timeframe = :tf "
            "and day = date '2001-01-01'"
        ),
        {"a": asset_id, "tf": timeframe},
    )
    return dict(row.mappings().one())


async def test_daily_counts_equal_the_raw_signals_and_can_be_recounted(
    session: AsyncSession,
) -> None:
    btc = await repo.get_asset(session, "BTC")
    model = await model_version(session, btc.id, "1m")
    # Candle closes minute by minute; signal i is made at minute i for minute i + 1.
    closes = ["100", "101", "101", "100.5", "102", "101", "103"]
    await repo.upsert_candles(
        session, btc.id, "1m", [candle(T0 + i * MINUTE, c) for i, c in enumerate(closes)]
    )
    calls = [
        ("up", 0.62),
        ("down", 0.40),
        ("down", 0.38),
        ("neutral", 0.51),
        ("up", 0.70),
        ("up", 0.58),
    ]
    for i, (label, p_up) in enumerate(calls):
        await session.execute(
            text(
                "insert into predictions (asset_id, timeframe, base_open_time, target_open_time, "
                "base_close, p_ml, p_up, label, model_version_id, feature_values) values "
                "(:a, '1m', :base, :target, :close, :p, :p, :label, :m, cast(:v as real[]))"
            ),
            {
                "a": btc.id, "base": T0 + i * MINUTE, "target": T0 + (i + 1) * MINUTE,
                "close": Decimal(closes[i]), "p": p_up, "label": label, "m": model, "v": [1.0],
            },
        )  # fmt: skip
    now = T0 + timedelta(hours=2)
    await resolve_outcomes(session, ["1m"], now=now, look_back=timedelta(days=1))

    day_end = T0 + timedelta(days=1)
    result = await stats.summarize_signals(session, since=T0, until=day_end)
    assert result["days"] >= 1
    row = await day_row(session, btc.id, "1m")

    # The same thing worked out by hand, signal by signal. Minute 2 closes flat (101 -> 101).
    moves = ["up", "flat", "down", "up", "down", "up"]  # close[i+1] against close[i]
    prev_up = [None, True, False, False, True, False]  # close[i] against close[i-1]
    expected = totals_of(
        [
            Resolved(np.float32(p_up).item(), label, move, before)
            for (label, p_up), move, before in zip(calls, moves, prev_up, strict=True)
            if move != "flat"
        ]
    )
    assert row["n_signals"] == 6 and row["n_flat"] == 1 and row["n_resolved"] == 5
    assert (row["n_went_up"], row["n_calls"], row["n_correct"]) == (3, 4, 3)
    for name in ("n_up_calls", "n_up_correct", "n_down_calls", "n_down_correct"):
        assert row[name] == getattr(expected, name), name
    assert (row["n_naive"], row["n_naive_correct"]) == (expected.n_naive, expected.n_naive_correct)
    assert row["brier_sum"] == pytest.approx(expected.brier_sum, rel=1e-6)

    # The endpoint's reader adds the days up to the same numbers.
    first_until = await session.execute(
        text(
            "select coalesce(sum(n_signals), 0) from signal_stats_daily where asset_id = :a "
            "and timeframe = '1m' and day = date '2001-01-01'"
        ),
        {"a": btc.id},
    )
    assert first_until.scalar_one() == 6

    # Counting again changes nothing (idempotent) ...
    await stats.summarize_signals(session, since=T0, until=day_end)
    again = await day_row(session, btc.id, "1m")
    assert {k: v for k, v in again.items() if k != "updated_at"} == {
        k: v for k, v in row.items() if k != "updated_at"
    }
    # ... and a late result is picked up by the next count.
    await repo.upsert_candles(session, btc.id, "1m", [candle(T0 + 7 * MINUTE, "104")])
    await signal(session, btc.id, model, "1m", T0 + 6 * MINUTE, "up", 0.6)
    await resolve_outcomes(session, ["1m"], now=now, look_back=timedelta(days=1))
    await stats.summarize_signals(session, since=T0, until=day_end)
    assert (await day_row(session, btc.id, "1m"))["n_signals"] == 7


async def test_clean_up_deletes_only_old_fast_rows_whose_day_is_counted(
    session: AsyncSession,
) -> None:
    btc = await repo.get_asset(session, "BTC")
    fast, slow = (
        await model_version(session, btc.id, "1m"),
        await model_version(session, btc.id, "1h"),
    )
    counted_day, uncounted_day = T0, T0 + timedelta(days=1)
    await repo.upsert_candles(
        session,
        btc.id,
        "1m",
        [candle(counted_day + MINUTE, "101"), candle(uncounted_day + MINUTE, "101")],
    )
    await repo.upsert_candles(
        session, btc.id, "1h", [candle(counted_day + timedelta(hours=1), "101")]
    )
    old_fast = await signal(session, btc.id, fast, "1m", counted_day, "up", 0.6)
    not_counted = await signal(session, btc.id, fast, "1m", uncounted_day, "up", 0.6)
    old_slow = await signal(session, btc.id, slow, "1h", counted_day, "up", 0.6)
    await resolve_outcomes(
        session, ["1m", "1h"], now=T0 + timedelta(days=2), look_back=timedelta(days=3)
    )
    # Only the first day is counted (the worker would have counted both; this is the unsafe case).
    await stats.summarize_signals(session, since=counted_day, until=uncounted_day)
    await session.execute(
        text("update signal_stats_daily set updated_at = :t where day = date '2001-01-01'"),
        {"t": T0 + timedelta(days=3)},
    )

    result = await stats.prune_fast_history(session, keep_days=90, now=T0 + timedelta(days=200))
    assert result["signals"] == 1 and result["older_than"] == "2001-04-21"
    left = await session.execute(
        text("select id from predictions where id = any(:ids)"),
        {"ids": [old_fast, not_counted, old_slow]},
    )
    assert {r[0] for r in left} == {not_counted, old_slow}  # uncounted day kept, 1h never touched
    outcome = await session.execute(
        text("select count(*) from prediction_outcomes where prediction_id = :id"), {"id": old_fast}
    )
    assert outcome.scalar_one() == 0  # its result went with it
    kept = await session.execute(
        text(
            "select timeframe, count(*) from candles where asset_id = :a and open_time < :end "
            "group by 1"
        ),
        {"a": btc.id, "end": T0 + timedelta(days=30)},
    )
    assert dict(kept.all()) == {"1h": 1}  # old 1m candles are gone, the 1h candle stays
    # The counts of the deleted day are still there: the track record lost nothing.
    assert (await day_row(session, btc.id, "1m"))["n_signals"] == 1

    # Nothing recent is ever touched.
    assert (await stats.prune_fast_history(session, keep_days=90, now=T0 + timedelta(days=200)))[
        "signals"
    ] == 0


def exact(value: float) -> Decimal:
    """A float as the same decimal number its shortest text form shows."""
    return Decimal(str(float(value)))


class OneModelCache:
    def __init__(self, bundle: ModelBundle) -> None:
        self._bundle = bundle

    async def get(self, path: str) -> ModelBundle:
        return self._bundle


def minute_frame(n: int, end: datetime, seed: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.0006, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    volume = rng.uniform(1, 50, n)
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * 1.0003,
            "low": np.minimum(open_, close) * 0.9997,
            "close": close,
            "volume": volume,
            "trades": rng.integers(5, 300, n).astype(float),
            "taker_buy_volume": volume * rng.uniform(0.3, 0.7, n),
        },
        index=pd.date_range(end=end, periods=n, freq="min", tz="UTC"),
    )


async def test_minute_prediction_job_runs_on_the_real_tables(session: AsyncSession) -> None:
    """The real `run_predictions` for 1m: one read for all coins, a model with order-flow
    features, and the compact snapshot. This one works at the current minute, so it first
    puts made-up BTC candles there and makes its own model the active one (all rolled back)."""
    now = datetime.now(UTC)
    expected = last_closed_open_time(now, "1m")
    frame = minute_frame(1300, expected)
    options = {"quiet_safe": True, "extended": True}
    data = build_dataset(frame, skip_flat=True, **options)
    params = XGB_PARAMS | {"n_estimators": 20, "early_stopping_rounds": 5}
    model = fit_calibrated(
        labelled(data.iloc[:500]),
        labelled(data.iloc[500:700]),
        labelled(data.iloc[700:]),
        feature_columns(data),
        params,
    )
    bundle = ModelBundle(
        model, "BTC", "1m", "test", data.index[0], data.index[499], feature_options=options
    )

    btc = await repo.get_asset(session, "BTC")
    await session.execute(
        text("update model_versions set is_active = false where timeframe = '1m'")
    )
    await session.execute(
        text(
            "insert into model_versions (asset_id, timeframe, train_start, train_end, "
            "artifact_path, is_active, feature_names) "
            "values (:a, '1m', :t, :t, 'test/none.joblib', true, cast(:names as text[]))"
        ),
        {"a": btc.id, "t": T0, "names": list(model.features)},
    )
    await repo.upsert_candles(
        session,
        btc.id,
        "1m",
        [
            Candle(
                t.to_pydatetime(), exact(r.open), exact(r.high),
                exact(r.low), exact(r.close), exact(r.volume),
                trades=int(r.trades), taker_buy_volume=exact(r.taker_buy_volume),
            )
            for t, r in zip(frame.index, frame.itertuples(), strict=True)
        ],
    )  # fmt: skip
    target = expected + MINUTE
    await session.execute(
        text("delete from predictions where timeframe = '1m' and target_open_time = :t"),
        {"t": target},
    )

    result = await run_predictions(session, OneModelCache(bundle), ["1m"], now)
    assert result == {"created": 1, "skipped": 0, "errors": []}
    row = (
        await session.execute(
            text(
                "select p.label, p.p_up, p.base_open_time, p.base_close, p.features, "
                "p.feature_values, v.features as through_view from predictions p "
                "join prediction_features v on v.prediction_id = p.id "
                "where p.asset_id = :a and p.timeframe = '1m' and p.target_open_time = :t"
            ),
            {"a": btc.id, "t": target},
        )
    ).one()
    assert row.label in ("up", "down", "neutral") and 0.01 <= row.p_up <= 0.99
    assert row.base_open_time == expected
    assert row.base_close == exact(frame["close"].iloc[-1])  # the exact stored close
    assert row.features is None and len(row.feature_values) == len(model.features)  # compact
    shown = row.through_view if isinstance(row.through_view, dict) else json.loads(row.through_view)
    assert {"taker_share_20", "dist_ema200", "ret_288"} <= set(shown)
    # Run again in the same minute: the unique key keeps it to one signal.
    second = await run_predictions(session, OneModelCache(bundle), ["1m"], now)
    assert second["created"] == 0 and second["errors"] == []
