"""Binance public market-data client (no API key, read-only endpoints)."""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx

from app.data.exchanges.base import Candle, ExchangeClient, ExchangeError
from app.timeframes import TIMEFRAMES

MAX_PAGE = 1000  # Binance returns at most 1000 klines per request
DEFAULT_LATEST = 500
MAX_RETRY_DELAY = 60.0  # seconds; a longer wait means something is wrong, so we stop instead


def _to_ms(moment: datetime) -> int:
    if moment.tzinfo is None:
        raise ValueError("datetimes passed to the exchange client must be timezone-aware (UTC)")
    return int(moment.timestamp() * 1000)


def _from_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=UTC)


def _parse(row: list[Any]) -> Candle:
    # Kline row: [open time, open, high, low, close, volume, close time, ...]
    # Prices arrive as strings, which lets us build exact Decimals.
    return Candle(
        open_time=_from_ms(row[0]),
        open=Decimal(row[1]),
        high=Decimal(row[2]),
        low=Decimal(row[3]),
        close=Decimal(row[4]),
        volume=Decimal(row[5]),
    )


class BinanceClient(ExchangeClient):
    name = "binance"

    def __init__(
        self,
        base_url: str,
        *,
        http: httpx.AsyncClient | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        max_retries: int = 4,
        page_pause: float = 0.2,
    ) -> None:
        self._http = http or httpx.AsyncClient(base_url=base_url, timeout=20.0)
        self._sleep = sleep  # injectable so tests do not really wait
        self._max_retries = max_retries
        self._page_pause = page_pause

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET with retries: network errors, 5xx and 429 (rate limit) are retried with backoff."""
        for attempt in range(self._max_retries + 1):
            last_try = attempt == self._max_retries
            backoff = float(2**attempt)
            try:
                response = await self._http.get(path, params=params)
            except httpx.TransportError as exc:
                if last_try:
                    raise ExchangeError(f"{self.name}: network error on {path}: {exc}") from exc
                await self._sleep(backoff)
                continue

            status = response.status_code
            if status == 418:
                # 418 = this IP is banned for ignoring 429s. Retrying makes the ban longer.
                raise ExchangeError(f"{self.name}: IP banned (HTTP 418) on {path}")
            if status == 429 or status >= 500:
                # Retry-After tells us how long the exchange wants us to wait.
                delay = float(response.headers.get("Retry-After", backoff))
                if last_try or delay > MAX_RETRY_DELAY:
                    raise ExchangeError(f"{self.name}: HTTP {status} on {path}, giving up")
                await self._sleep(delay)
                continue
            if status >= 400:
                raise ExchangeError(f"{self.name}: HTTP {status} on {path}: {response.text[:200]}")
            return response.json()
        raise ExchangeError(f"{self.name}: no response from {path}")  # pragma: no cover

    async def _server_time_ms(self) -> int:
        # We compare candle close times with the exchange's clock, not ours, so a wrong
        # local clock can never make an open candle look closed.
        return int((await self._get("/api/v3/time"))["serverTime"])

    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Candle]:
        step = TIMEFRAMES[timeframe]
        now_ms = await self._server_time_ms()
        base = {"symbol": symbol, "interval": timeframe}

        def closed(rows: list[list[Any]]) -> list[Candle]:
            # row[6] is the close time. A candle that has not closed yet is still changing
            # and must never reach the database or the model (docs/03, no data leakage).
            return [_parse(row) for row in rows if row[6] < now_ms]

        if start is None:
            wanted = min(limit or DEFAULT_LATEST, MAX_PAGE - 1)
            params = {**base, "limit": wanted + 1}  # +1 because the newest row is still open
            if end is not None:
                params["endTime"] = _to_ms(end)
            return closed(await self._get("/api/v3/klines", params))[-wanted:]

        candles: list[Candle] = []
        cursor_ms = _to_ms(start)
        stop_ms = min(_to_ms(end), now_ms) if end is not None else now_ms
        while cursor_ms <= stop_ms:
            params = {**base, "startTime": cursor_ms, "endTime": stop_ms, "limit": MAX_PAGE}
            rows = await self._get("/api/v3/klines", params)
            if not rows:
                break
            candles.extend(closed(rows))
            if limit is not None and len(candles) >= limit:
                return candles[:limit]
            if len(rows) < MAX_PAGE:
                break  # a short page means we reached the end
            # Next page starts one candle after the last one we received.
            cursor_ms = rows[-1][0] + int(step.total_seconds() * 1000)
            await self._sleep(self._page_pause)  # stay far below the rate limit
        return candles

    async def get_last_price(self, symbol: str) -> Decimal:
        data = await self._get("/api/v3/ticker/price", {"symbol": symbol})
        return Decimal(data["price"])
