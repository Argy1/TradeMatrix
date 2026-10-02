"""The candle sizes TradeMatrix supports (docs/01)."""

from datetime import UTC, datetime, timedelta
from typing import Literal

Timeframe = Literal["1h", "4h", "1d"]

TIMEFRAMES: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def is_aligned(open_time: datetime, timeframe: str) -> bool:
    """True if `open_time` is a valid candle start, e.g. 4h candles open at 00, 04, 08... UTC."""
    return (open_time - _EPOCH) % TIMEFRAMES[timeframe] == timedelta(0)
