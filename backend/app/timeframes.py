"""The candle sizes TradeMatrix supports (docs/01). Everything about a size is derived from
the two tables below, so adding a size means adding one line here (plus the database check)."""

from datetime import UTC, datetime, timedelta
from typing import Literal

Timeframe = Literal["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d"]

# Fast sizes (Phase 5b): predicted by the every-minute pipeline. Binance has no 10m candle, so
# 15m takes its place.
FAST_TIMEFRAMES: dict[str, timedelta] = {
    "1m": timedelta(minutes=1),
    "3m": timedelta(minutes=3),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
}

# Slow sizes: predicted by the hourly pipeline.
SLOW_TIMEFRAMES: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

# Every size, shortest first (also the order the apps show them in).
TIMEFRAMES: dict[str, timedelta] = FAST_TIMEFRAMES | SLOW_TIMEFRAMES

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_UNIT_WORDS = {"m": "minute", "h": "hour", "d": "day"}


def is_aligned(open_time: datetime, timeframe: str) -> bool:
    """True if `open_time` is a valid candle start, e.g. 4h candles open at 00, 04, 08... UTC."""
    return (open_time - _EPOCH) % TIMEFRAMES[timeframe] == timedelta(0)


def floor_time(moment: datetime, timeframe: str) -> datetime:
    """Open time of the candle that contains `moment`."""
    return moment - (moment - _EPOCH) % TIMEFRAMES[timeframe]


def last_closed_open_time(now: datetime, timeframe: str) -> datetime:
    """Open time of the newest candle that has already closed at `now`."""
    return floor_time(now, timeframe) - TIMEFRAMES[timeframe]


def timeframe_words(timeframe: str) -> str:
    """'15m' -> '15 minute', as in "the next 15 minute candle"."""
    return f"{timeframe[:-1]} {_UNIT_WORDS[timeframe[-1]]}"


def stale_grace(timeframe: str) -> timedelta:
    """How long after a close the new candle (or signal) may still be on its way.

    Three minutes for the slow sizes. A fast candle gets half its own length: with three
    minutes, three missed one-minute signals would go unnoticed.
    """
    return min(timedelta(minutes=3), TIMEFRAMES[timeframe] / 2)


def interval_case_sql(column: str) -> str:
    """SQL for "the length of the candle in this row", e.g. `p.base_open_time - <this>` is the
    candle before. Built from the table above (fixed values, never user input), so a query can
    not forget a size."""
    whens = " ".join(
        f"when '{timeframe}' then interval '{int(length.total_seconds())} seconds'"
        for timeframe, length in TIMEFRAMES.items()
    )
    return f"(case {column} {whens} end)"
