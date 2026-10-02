"""Exchange adapter interface.

The rest of the backend only talks to `ExchangeClient`, never to Binance directly.
Why: if Binance becomes unreachable we add one new file (bybit.py, okx.py...) and
change the EXCHANGE variable, without touching ingestion, features or the API.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class ExchangeError(Exception):
    """The exchange could not be reached or returned an error we cannot recover from."""


@dataclass(frozen=True, slots=True)
class Candle:
    """One closed OHLCV candle. Prices are Decimal so no precision is lost before Postgres."""

    open_time: datetime  # timezone-aware, UTC
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class ExchangeClient(ABC):
    name: str

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Candle]:
        """Return CLOSED candles only, oldest first.

        With `start`: every closed candle whose open time is in [start, end], paginating as
        needed (`limit` caps the total). Without `start`: the most recent `limit` closed candles.
        """

    @abstractmethod
    async def get_last_price(self, symbol: str) -> Decimal:
        """Latest traded price (used for price alerts and the markets list)."""

    def stream_klines(self, symbols: Sequence[str], timeframe: str) -> AsyncIterator[dict]:
        """Live candle updates over WebSocket. Implemented in Phase 3."""
        raise NotImplementedError

    async def aclose(self) -> None:  # noqa: B027 - optional hook, not every client holds resources
        """Release network resources."""
