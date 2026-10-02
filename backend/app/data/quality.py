"""Data-quality checks for candles (docs/03): duplicates, gaps and impossible values."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime

from app.data.exchanges.base import Candle
from app.timeframes import TIMEFRAMES, is_aligned


@dataclass
class QualityReport:
    duplicates: list[datetime] = field(default_factory=list)
    # Open times that should exist between two candles but are missing.
    gaps: list[datetime] = field(default_factory=list)
    invalid: list[tuple[datetime, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.duplicates or self.gaps or self.invalid)

    def summary(self) -> str:
        return (
            f"duplicates={len(self.duplicates)} gaps={len(self.gaps)} invalid={len(self.invalid)}"
        )


def _problem(candle: Candle, timeframe: str) -> str | None:
    if not is_aligned(candle.open_time, timeframe):
        return "open_time is not on a candle boundary"
    if candle.high < max(candle.open, candle.close):
        return "high is below open/close"
    if candle.low > min(candle.open, candle.close):
        return "low is above open/close"
    if candle.volume < 0:
        return "negative volume"
    return None


def check_candles(candles: Sequence[Candle], timeframe: str) -> QualityReport:
    """Check candles that are sorted by open time (oldest first)."""
    step = TIMEFRAMES[timeframe]
    report = QualityReport()
    previous: datetime | None = None
    for candle in candles:
        problem = _problem(candle, timeframe)
        if problem:
            report.invalid.append((candle.open_time, problem))
        if previous is not None:
            if candle.open_time == previous:
                report.duplicates.append(candle.open_time)
            else:
                missing = previous + step
                while missing < candle.open_time:
                    report.gaps.append(missing)
                    missing += step
        previous = candle.open_time
    return report


def valid_candles(candles: Sequence[Candle], timeframe: str) -> list[Candle]:
    """Drop candles the table would reject, keeping the first of any duplicates."""
    seen: set[datetime] = set()
    kept: list[Candle] = []
    for candle in candles:
        if candle.open_time in seen or _problem(candle, timeframe):
            continue
        seen.add(candle.open_time)
        kept.append(candle)
    return kept
