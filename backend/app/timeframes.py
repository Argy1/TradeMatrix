"""The candle sizes TradeMatrix supports (docs/01)."""

from datetime import UTC, datetime, timedelta
from typing import Literal

Timeframe = Literal["1h", "4h", "1d"]

# The sizes the live system serves (worker, API, apps).
TIMEFRAMES: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

# Fast sizes (Phase 5b). The history files and the backtest use them already; they move into
# TIMEFRAMES when the every-minute pipeline goes live. Binance has no 10m candle, so 15m
# takes its place.
FAST_TIMEFRAMES: dict[str, timedelta] = {
    "1m": timedelta(minutes=1),
    "3m": timedelta(minutes=3),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
}

# Every size the time maths below and the exchange client understand.
ALL_TIMEFRAMES: dict[str, timedelta] = FAST_TIMEFRAMES | TIMEFRAMES

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def is_aligned(open_time: datetime, timeframe: str) -> bool:
    """True if `open_time` is a valid candle start, e.g. 4h candles open at 00, 04, 08... UTC."""
    return (open_time - _EPOCH) % ALL_TIMEFRAMES[timeframe] == timedelta(0)


def floor_time(moment: datetime, timeframe: str) -> datetime:
    """Open time of the candle that contains `moment`."""
    return moment - (moment - _EPOCH) % ALL_TIMEFRAMES[timeframe]


def last_closed_open_time(now: datetime, timeframe: str) -> datetime:
    """Open time of the newest candle that has already closed at `now`."""
    return floor_time(now, timeframe) - ALL_TIMEFRAMES[timeframe]
