"""ingest_candles with a fake exchange and a fake table (a dict keyed like the primary key)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.data import ingest
from app.data.exchanges.base import Candle, ExchangeClient
from app.data.repo import Asset

BTC = Asset(id=1, symbol="BTC", name="Bitcoin", exchange_symbol="BTCUSDT")
NOW = datetime(2026, 10, 3, 14, 20, tzinfo=UTC)


def candle(open_time: datetime, high: str = "110") -> Candle:
    return Candle(
        open_time, Decimal("100"), Decimal(high), Decimal("90"), Decimal("105"), Decimal("1")
    )


class FakeExchange(ExchangeClient):
    name = "fake"

    def __init__(self, candles: list[Candle]) -> None:
        self.candles = candles
        self.starts: list[datetime] = []

    async def get_klines(self, symbol, timeframe, start=None, end=None, limit=None):
        self.starts.append(start)
        return [c for c in self.candles if c.open_time >= start]

    async def get_last_price(self, symbol):
        return Decimal("0")


class FakeSession:
    commits = 0

    async def commit(self) -> None:
        self.commits += 1


@pytest.fixture
def table(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Stands in for the candles table: the key is the primary key, so upserts cannot duplicate."""
    rows: dict[tuple[int, str, datetime], Candle] = {}

    async def latest_open_time(_session, asset_id, timeframe):
        times = [key[2] for key in rows if key[:2] == (asset_id, timeframe)]
        return max(times) if times else None

    async def upsert_candles(_session, asset_id, timeframe, candles):
        for c in candles:
            rows[(asset_id, timeframe, c.open_time)] = c
        return len(candles)

    monkeypatch.setattr(ingest.repo, "latest_open_time", latest_open_time)
    monkeypatch.setattr(ingest.repo, "upsert_candles", upsert_candles)
    return rows


async def test_first_run_backfills_from_the_configured_history_start(table: dict) -> None:
    exchange = FakeExchange([])
    await ingest.ingest_candles(FakeSession(), exchange, BTC, "1h", now=NOW)
    # 730 days back, rounded down to a candle boundary.
    assert exchange.starts == [datetime(2024, 10, 3, 14, 0, tzinfo=UTC)]


async def test_later_runs_continue_after_the_newest_stored_candle(table: dict) -> None:
    newest = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
    table[(1, "1h", newest)] = candle(newest)
    exchange = FakeExchange([candle(newest + timedelta(hours=1))])

    result = await ingest.ingest_candles(FakeSession(), exchange, BTC, "1h", now=NOW)

    assert exchange.starts == [newest + timedelta(hours=1)]
    assert (result.fetched, result.stored) == (1, 1)
    assert len(table) == 2


async def test_running_twice_stores_each_candle_once(table: dict) -> None:
    start = datetime(2024, 10, 3, 14, 0, tzinfo=UTC)
    exchange = FakeExchange([candle(start + timedelta(hours=i)) for i in range(48)])
    session = FakeSession()

    first = await ingest.ingest_candles(session, exchange, BTC, "1h", now=NOW)
    second = await ingest.ingest_candles(session, exchange, BTC, "1h", now=NOW)

    assert first.stored == 48
    assert second.stored == 0  # nothing new, nothing duplicated
    assert len(table) == 48
    assert session.commits == 2


async def test_invalid_candles_are_reported_but_not_stored(table: dict) -> None:
    start = datetime(2024, 10, 3, 14, 0, tzinfo=UTC)
    bad = candle(start + timedelta(hours=1), high="101")  # high below the close of 105
    exchange = FakeExchange([candle(start), bad, candle(start + timedelta(hours=2))])

    result = await ingest.ingest_candles(FakeSession(), exchange, BTC, "1h", now=NOW)

    assert (result.fetched, result.stored) == (3, 2)
    assert len(result.quality.invalid) == 1
    assert bad.open_time not in {key[2] for key in table}
