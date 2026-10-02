"""BinanceClient against a fake exchange (httpx.MockTransport), plus one optional live call."""

import itertools
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from app.config import Settings
from app.data.exchanges.base import ExchangeError
from app.data.exchanges.binance import BinanceClient

HOUR_MS = 3_600_000
BASE_MS = 1_700_000_000_000 - (1_700_000_000_000 % HOUR_MS)  # an exact hour boundary
BASE = datetime.fromtimestamp(BASE_MS / 1000, tz=UTC)


def row(open_ms: int) -> list:
    return [open_ms, "100.10", "110.00", "90.00", "105.55", "12.5", open_ms + HOUR_MS - 1]


class FakeBinance:
    """Serves 1h klines starting at BASE; `now_ms` decides which candle is still open."""

    def __init__(self, now_ms: int, fail_with: list[httpx.Response] | None = None) -> None:
        self.now_ms = now_ms
        self.fail_with = fail_with or []  # responses to send before behaving normally
        self.kline_calls: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v3/time":
            return httpx.Response(200, json={"serverTime": self.now_ms})
        if request.url.path == "/api/v3/ticker/price":
            return httpx.Response(200, json={"symbol": "BTCUSDT", "price": "67123.45000000"})

        query = dict(request.url.params)
        self.kline_calls.append(query)
        if self.fail_with:
            return self.fail_with.pop(0)
        limit = int(query["limit"])
        current_open = self.now_ms - (self.now_ms % HOUR_MS)  # the candle that is still forming
        if "startTime" in query:
            first = max(int(query["startTime"]), BASE_MS)
            first += (-first) % HOUR_MS  # round up to a candle boundary
            last = min(int(query["endTime"]), current_open)
            opens = list(range(first, last + 1, HOUR_MS))[:limit]
        else:
            opens = list(range(current_open - (limit - 1) * HOUR_MS, current_open + 1, HOUR_MS))
        return httpx.Response(200, json=[row(o) for o in opens])


def make_client(fake: FakeBinance) -> tuple[BinanceClient, list[float]]:
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    http = httpx.AsyncClient(base_url="https://fake.exchange", transport=httpx.MockTransport(fake))
    return BinanceClient("https://fake.exchange", http=http, sleep=fake_sleep), sleeps


async def test_pagination_returns_every_closed_candle_once() -> None:
    # 2500 closed candles exist, and candle number 2501 is 30 minutes into forming.
    fake = FakeBinance(now_ms=BASE_MS + 2500 * HOUR_MS + HOUR_MS // 2)
    client, _ = make_client(fake)

    candles = await client.get_klines("BTCUSDT", "1h", start=BASE)

    assert len(candles) == 2500
    assert len(fake.kline_calls) == 3  # 1000 + 1000 + the rest
    times = [c.open_time for c in candles]
    assert times[0] == BASE
    assert all(b - a == timedelta(hours=1) for a, b in itertools.pairwise(times))


async def test_open_candle_is_never_returned() -> None:
    fake = FakeBinance(now_ms=BASE_MS + 10 * HOUR_MS + 1)
    client, _ = make_client(fake)

    latest = await client.get_klines("BTCUSDT", "1h", limit=5)

    assert len(latest) == 5
    still_forming = BASE + timedelta(hours=10)
    assert latest[-1].open_time == still_forming - timedelta(hours=1)
    assert all(c.open_time < still_forming for c in latest)


async def test_prices_are_exact_decimals() -> None:
    client, _ = make_client(FakeBinance(now_ms=BASE_MS + 3 * HOUR_MS + 1))

    candle = (await client.get_klines("BTCUSDT", "1h", limit=1))[0]

    assert candle.close == Decimal("105.55")
    assert candle.open_time.tzinfo is UTC
    assert await client.get_last_price("BTCUSDT") == Decimal("67123.45000000")


async def test_limit_caps_a_paginated_request() -> None:
    client, _ = make_client(FakeBinance(now_ms=BASE_MS + 2500 * HOUR_MS + 1))
    assert len(await client.get_klines("BTCUSDT", "1h", start=BASE, limit=1200)) == 1200


async def test_rate_limit_waits_for_retry_after_then_succeeds() -> None:
    fake = FakeBinance(
        now_ms=BASE_MS + 5 * HOUR_MS + 1,
        fail_with=[httpx.Response(429, headers={"Retry-After": "2"})],
    )
    client, sleeps = make_client(fake)

    candles = await client.get_klines("BTCUSDT", "1h", limit=3)

    assert len(candles) == 3
    assert sleeps == [2.0]


async def test_ban_and_client_errors_raise() -> None:
    for status in (418, 400):
        fake = FakeBinance(now_ms=BASE_MS + HOUR_MS, fail_with=[httpx.Response(status, text="no")])
        client, sleeps = make_client(fake)
        with pytest.raises(ExchangeError):
            await client.get_klines("BTCUSDT", "1h", limit=3)
        assert sleeps == []  # these are not retried


async def test_server_errors_give_up_after_retries() -> None:
    fake = FakeBinance(now_ms=BASE_MS + HOUR_MS, fail_with=[httpx.Response(503)] * 10)
    client, sleeps = make_client(fake)
    with pytest.raises(ExchangeError):
        await client.get_klines("BTCUSDT", "1h", limit=3)
    assert sleeps == [1.0, 2.0, 4.0, 8.0]  # exponential backoff, then stop


async def test_naive_datetime_is_rejected() -> None:
    client, _ = make_client(FakeBinance(now_ms=BASE_MS + HOUR_MS))
    with pytest.raises(ValueError, match="timezone-aware"):
        await client.get_klines("BTCUSDT", "1h", start=datetime(2024, 1, 1))


@pytest.mark.live
async def test_live_exchange_returns_contiguous_closed_candles() -> None:
    """Real network call. Run with: uv run pytest -m live"""
    client = BinanceClient(Settings().binance_rest_url)
    try:
        candles = await client.get_klines("BTCUSDT", "1h", limit=5)
    finally:
        await client.aclose()
    assert len(candles) == 5
    assert candles[-1].open_time + timedelta(hours=1) <= datetime.now(UTC) + timedelta(minutes=1)
    assert all(
        b.open_time - a.open_time == timedelta(hours=1) for a, b in itertools.pairwise(candles)
    )
