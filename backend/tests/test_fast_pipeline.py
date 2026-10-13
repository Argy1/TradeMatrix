"""The every-minute pipeline (Phase 5b): reading many coins at once, the exchange clock, the
track-record maths on counts, and the order-flow reason. No database needed."""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pandas as pd
import pytest

from app.alerts.rules import Signal, signal_notification
from app.data import ingest, repo
from app.data.exchanges.base import Candle, ExchangeClient, ExchangeError
from app.data.exchanges.binance import BinanceClient
from app.data.repo import Asset
from app.ml.performance import Resolved, Totals, from_totals, performance, totals_of
from app.ml.predict import FrameCache
from app.ml.reasons import build_reasons
from app.timeframes import TIMEFRAMES, interval_case_sql, stale_grace, timeframe_words

NOW = datetime(2026, 10, 11, 12, 5, 2, tzinfo=UTC)  # two seconds after the 12:05 close
BTC = Asset(id=1, symbol="BTC", name="Bitcoin", exchange_symbol="BTCUSDT")
ETH = Asset(id=2, symbol="ETH", name="Ethereum", exchange_symbol="ETHUSDT")
SOL = Asset(id=3, symbol="SOL", name="Solana", exchange_symbol="SOLUSDT")


def candle(open_time: datetime) -> Candle:
    return Candle(open_time, Decimal("100"), Decimal("110"), Decimal("90"), Decimal("105"),
                  Decimal("2"), trades=40, taker_buy_volume=Decimal("1.1"))  # fmt: skip


class Exchange(ExchangeClient):
    """Serves one-minute and five-minute candles up to `newest`; records every request."""

    name = "fake"

    def __init__(self, newest: dict[str, datetime], broken: str = "", late: str = "") -> None:
        self.newest, self.broken, self.late = newest, broken, late
        self.requests: list[tuple[str, str, datetime]] = []

    async def get_klines(self, symbol, timeframe, start=None, end=None, limit=None):
        self.requests.append((symbol, timeframe, start))
        if symbol == self.broken:
            raise ExchangeError("fake: HTTP 500")
        newest = self.newest[timeframe]
        asked_before = sum(1 for s, tf, _ in self.requests if (s, tf) == (symbol, timeframe))
        if symbol == self.late and asked_before == 1:
            newest -= TIMEFRAMES[timeframe]  # the first answer does not have the new candle yet
        out, moment = [], start
        while moment <= newest:
            out.append(candle(moment))
            moment += TIMEFRAMES[timeframe]
        return out

    async def get_last_price(self, symbol):
        return Decimal("0")


@pytest.fixture
def table(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Stands in for the candles table: the key is the primary key."""

    class Table(dict):
        trips: list[int]

    rows: dict[tuple[int, str, datetime], Candle] = Table()

    async def latest_open_times(_session, timeframes):
        found = {}
        for asset in (BTC, ETH, SOL):
            for tf in timeframes:
                times = [k[2] for k in rows if k[:2] == (asset.id, tf)]
                found[(asset.id, tf)] = max(times) if times else None
        return found

    trips: list[int] = []

    async def upsert_many(_session, batches):
        trips.append(len(batches))
        for asset_id, timeframe, candles in batches:
            for c in candles:
                rows[(asset_id, timeframe, c.open_time)] = c
        return sum(len(candles) for _, _, candles in batches)

    monkeypatch.setattr(ingest.repo, "latest_open_times", latest_open_times)
    monkeypatch.setattr(ingest.repo, "upsert_many", upsert_many)
    rows.trips = trips  # how many times the "database" was written to
    return rows


def at(hour: int, minute: int) -> datetime:
    return datetime(2026, 10, 11, hour, minute, tzinfo=UTC)


NEWEST = {"1m": at(12, 4), "5m": at(12, 0)}  # the candles that closed at 12:05:00


async def no_wait(_seconds: float) -> None:
    return None


async def test_all_coins_are_read_in_one_go_and_only_what_is_missing(table: dict) -> None:
    for asset in (BTC, ETH, SOL):  # everything up to 12:03 (1m) and 11:55 (5m) is stored
        table[(asset.id, "1m", at(12, 3))] = candle(at(12, 3))
        table[(asset.id, "5m", at(11, 55))] = candle(at(11, 55))
    exchange = Exchange(NEWEST)
    result = await ingest.ingest_many(None, exchange, [BTC, ETH, SOL], ["1m", "5m"], now=NOW)
    assert result == {"timeframes": ["1m", "5m"], "stored": 6, "retried": 0, "errors": []}
    assert len(exchange.requests) == 6  # one per coin and size
    assert table.trips == [6]  # all six batches stored in ONE trip to the database
    assert {start for _, tf, start in exchange.requests if tf == "1m"} == {at(12, 4)}
    assert table[(2, "5m", at(12, 0))].trades == 40  # order flow is stored with the candle

    # Run again in the same minute: nothing is missing, so the exchange is not asked at all.
    again = await ingest.ingest_many(None, exchange, [BTC, ETH, SOL], ["1m", "5m"], now=NOW)
    assert again["stored"] == 0 and len(exchange.requests) == 6


async def test_one_failing_coin_does_not_stop_the_others(table: dict) -> None:
    for asset in (BTC, ETH, SOL):
        table[(asset.id, "1m", at(12, 3))] = candle(at(12, 3))
    exchange = Exchange(NEWEST, broken="ETHUSDT")
    result = await ingest.ingest_many(None, exchange, [BTC, ETH, SOL], ["1m"], now=NOW)
    assert result["stored"] == 2
    assert result["errors"] == ["ETH 1m: ExchangeError: fake: HTTP 500"]
    assert (1, "1m", at(12, 4)) in table and (3, "1m", at(12, 4)) in table


async def test_a_candle_that_is_not_served_yet_is_asked_for_once_more(table: dict) -> None:
    for asset in (BTC, SOL):
        table[(asset.id, "1m", at(12, 3))] = candle(at(12, 3))
    exchange = Exchange(NEWEST, late="SOLUSDT")
    waits: list[float] = []

    async def sleep(seconds: float) -> None:
        waits.append(seconds)

    result = await ingest.ingest_many(None, exchange, [BTC, SOL], ["1m"], now=NOW, sleep=sleep)
    assert result["stored"] == 2 and result["errors"] == [] and result["retried"] == 1
    assert waits == [ingest.RETRY_AFTER]  # only the late coin waited, and only once
    assert [s for s, _, _ in exchange.requests].count("SOLUSDT") == 2


async def test_a_new_size_starts_with_enough_candles_for_the_chart(table: dict) -> None:
    exchange = Exchange(NEWEST)
    await ingest.ingest_many(None, exchange, [BTC], ["1m"], now=NOW, sleep=no_wait)
    assert exchange.requests[0][2] == at(12, 5) - timedelta(days=ingest.BACKFILL_DAYS["1m"])
    assert set(ingest.BACKFILL_DAYS) == set(TIMEFRAMES)
    for timeframe, days in ingest.BACKFILL_DAYS.items():
        assert timedelta(days=days) / TIMEFRAMES[timeframe] >= 1500, timeframe


# ---------------------------------------------------------------- exchange clock
async def test_exchange_clock_is_asked_once_and_never_runs_ahead() -> None:
    server_ms = 1_791_730_000_000
    asked = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal asked
        if request.url.path == "/api/v3/time":
            asked += 1
            return httpx.Response(200, json={"serverTime": server_ms})
        return httpx.Response(200, json=[])

    http = httpx.AsyncClient(
        base_url="https://fake.exchange", transport=httpx.MockTransport(handler)
    )
    client = BinanceClient("https://fake.exchange", http=http)
    readings = [await client._server_time_ms() for _ in range(5)]
    for _ in range(3):
        await client.get_klines("BTCUSDT", "1m", limit=2)
    assert asked == 1  # remembered for 30 seconds: 8 uses, one request
    assert readings == sorted(readings)
    assert 0 <= readings[-1] - server_ms < 2_000  # it follows our clock from the measured point
    await client.aclose()


async def test_sixteen_coins_starting_together_ask_the_clock_once() -> None:
    asked = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal asked
        if request.url.path == "/api/v3/time":
            asked += 1
            return httpx.Response(200, json={"serverTime": 1_791_730_000_000})
        return httpx.Response(200, json=[])

    http = httpx.AsyncClient(
        base_url="https://fake.exchange", transport=httpx.MockTransport(handler)
    )
    client = BinanceClient("https://fake.exchange", http=http)
    await asyncio.gather(*(client.get_klines(f"COIN{i}USDT", "1m", limit=2) for i in range(16)))
    assert asked == 1
    await client.aclose()


# ---------------------------------------------------------------- sizes
def test_every_size_has_words_a_grace_period_and_a_place_in_sql() -> None:
    assert [timeframe_words(tf) for tf in TIMEFRAMES] == [
        "1 minute", "3 minute", "5 minute", "15 minute", "30 minute", "1 hour", "4 hour", "1 day",
    ]  # fmt: skip
    assert stale_grace("1m") == timedelta(seconds=30)  # half a candle
    assert stale_grace("5m") == timedelta(seconds=150)
    assert stale_grace("15m") == stale_grace("1h") == stale_grace("1d") == timedelta(minutes=3)
    sql = interval_case_sql("p.timeframe")
    assert sql.startswith("(case p.timeframe when '1m' then interval '60 seconds'")
    assert "when '1d' then interval '86400 seconds' end)" in sql
    assert all(f"when '{tf}'" in sql for tf in TIMEFRAMES)


def test_alert_text_names_the_fast_candle() -> None:
    signal = Signal("up", 0.58, at(12, 5), previous_label="neutral")
    title, body, _ = signal_notification("BTC", "15m", "signal_change", None, signal)
    assert title == "BTC 15m signal changed to Up"
    assert "58.0% chance the next 15 minute candle closes higher." in body


# ---------------------------------------------------------------- track record on counts
ROWS = [
    Resolved(0.70, "up", "up", True),
    Resolved(0.60, "up", "down", True),
    Resolved(0.30, "down", "down", False),
    Resolved(0.50, "neutral", "up", None),
]


def test_counts_give_the_same_numbers_as_single_signals() -> None:
    counts = totals_of(ROWS)
    assert counts == Totals(
        n_resolved=4, n_went_up=2, n_calls=3, n_correct=2, n_up_calls=2, n_up_correct=1,
        n_down_calls=1, n_down_correct=1, n_naive=3, n_naive_correct=2,
        brier_sum=pytest.approx(0.09 + 0.36 + 0.09 + 0.25),
    )  # fmt: skip
    assert from_totals(counts) == performance(ROWS)
    stats = from_totals(counts)
    assert stats["baseline"]["always_up"] == 0.5 and stats["baseline"]["always_down"] == 0.5
    # The naive rule was right on 2 of the 3 rows it could answer, so reversing it gets 1 of 3.
    assert stats["baseline"]["naive"] == pytest.approx(2 / 3)
    assert stats["baseline"]["reverse"] == pytest.approx(1 / 3)
    assert stats["baseline"]["best"] == pytest.approx(2 / 3)
    assert stats["brier_baseline"] == 0.25


def test_days_add_up() -> None:
    """Two days counted separately and added give the numbers of both days together."""
    monday, tuesday = ROWS[:2], ROWS[2:]
    assert from_totals(totals_of(monday) + totals_of(tuesday)) == performance(ROWS)
    assert totals_of([]) + totals_of(ROWS) == totals_of(ROWS)


def test_no_signals_yet_is_explicit() -> None:
    stats = from_totals(Totals())
    assert stats["accuracy"] is None and stats["coverage"] is None and stats["brier"] is None
    assert set(stats["baseline"]) == {"naive", "reverse", "always_up", "always_down", "best"}
    assert all(value is None for value in stats["baseline"].values())
    assert stats["low_sample"] is True


# ---------------------------------------------------------------- reasons
FEATURES = {
    "rsi14": 50.0, "dist_ema50": 0.0, "atr_pct": 1.0, "ema_cross_3": 0.0, "macd_hist_pct": 0.0,
    "vol_ratio_20": 1.0, "bb_percent_b": 0.5, "ret_24": 0.0,
}  # fmt: skip


def test_order_flow_is_a_reason_when_one_side_was_clearly_more_active() -> None:
    importances = {"taker_share_20": 5.0}
    buyers = build_reasons(FEATURES | {"taker_share_20": 0.61}, importances)[0]
    assert buyers == {
        "code": "order_flow",
        "text": "Buyers were the more active side: 61% of the volume over the last 20 candles",
        "effect": "up",
    }
    sellers = build_reasons(FEATURES | {"taker_share_20": 0.42}, importances)[0]
    assert sellers["text"].startswith("Sellers were the more active side: 58%")
    assert sellers["effect"] == "down"
    # The slow models have no order flow: nothing changes for them.
    assert all(r["code"] != "order_flow" for r in build_reasons(FEATURES, {}))
    assert all(
        r["code"] != "order_flow"
        for r in build_reasons(FEATURES | {"taker_share_20": None}, importances)
    )


# ---------------------------------------------------------------- candles kept between runs
def frame(start_minute: int, count: int, last_close: str = "100") -> repo.FeatureFrame:
    index = pd.DatetimeIndex(
        [at(12, 0) + timedelta(minutes=start_minute + i) for i in range(count)]
    )
    values = {name: [float(start_minute + i) for i in range(count)] for name in FRAME_COLUMNS}
    return repo.FeatureFrame(pd.DataFrame(values, index=index), Decimal(last_close))


FRAME_COLUMNS = ["open", "high", "low", "close", "volume", "trades", "taker_buy_volume"]


async def test_candles_are_read_in_full_once_and_then_only_the_new_ones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = {1: 10, 2: 10}  # asset id -> how many one-minute candles the "database" has
    reads: list[datetime | None] = []

    async def feature_frames(_session, asset_ids, timeframe, limit, after=None):
        reads.append(after)
        out = {}
        for asset_id in asset_ids:
            full = frame(0, stored[asset_id], last_close=str(100 + stored[asset_id]))
            rows = full.frame if after is None else full.frame[full.frame.index > after]
            if len(rows):
                out[asset_id] = repo.FeatureFrame(rows.iloc[-limit:], full.last_close)
        return out

    monkeypatch.setattr(repo, "feature_frames", feature_frames)
    cache = FrameCache()

    first = await cache.get(None, [1, 2], "1m", 8)
    assert reads == [None] and len(first[1].frame) == 8  # everything, cut to the limit

    stored.update({1: 11, 2: 11})  # one more minute closed
    second = await cache.get(None, [1, 2], "1m", 8)
    assert reads[-1] == at(12, 9)  # asked only for candles after the newest one it holds
    assert len(second[1].frame) == 8 and second[1].frame.index[-1] == at(12, 10)
    assert second[1].last_close == Decimal("111")
    full = (await feature_frames(None, [1], "1m", 8))[1].frame
    pd.testing.assert_frame_equal(second[1].frame, full)  # the same as a full read

    # Nothing new: the held candles are returned as they are.
    third = await cache.get(None, [1, 2], "1m", 8)
    assert third[1].frame.index[-1] == at(12, 10) and third[2].last_close == Decimal("111")

    # A candle is missing between what is held and what is new: read everything again.
    async def with_a_gap(_session, asset_ids, timeframe, limit, after=None):
        reads.append(after)
        if after is None:
            return {asset_id: frame(0, 14) for asset_id in asset_ids}
        return {asset_id: frame(12, 2) for asset_id in asset_ids}  # minute 11 is missing

    monkeypatch.setattr(repo, "feature_frames", with_a_gap)
    before = len(reads)
    fourth = await cache.get(None, [1, 2], "1m", 8)
    assert reads[before:] == [at(12, 10), None]  # tried the short read, then the full one
    assert fourth[1].frame.index[-1] == at(12, 13)

    # A coin that is not held yet also means a full read.
    await cache.get(None, [1, 2, 3], "1m", 8)
    assert reads[-1] is None
