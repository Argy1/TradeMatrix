from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.data.exchanges.base import Candle
from app.data.quality import check_candles, valid_candles

T0 = datetime(2026, 1, 1, tzinfo=UTC)


def candle(hours: float, *, o="100", h="110", low="90", c="105", v="1") -> Candle:
    return Candle(
        open_time=T0 + timedelta(hours=hours),
        open=Decimal(o),
        high=Decimal(h),
        low=Decimal(low),
        close=Decimal(c),
        volume=Decimal(v),
    )


def test_clean_series_passes() -> None:
    report = check_candles([candle(0), candle(1), candle(2)], "1h")
    assert report.ok
    assert report.summary() == "duplicates=0 gaps=0 invalid=0"


def test_gap_lists_every_missing_open_time() -> None:
    report = check_candles([candle(0), candle(3)], "1h")
    assert report.gaps == [T0 + timedelta(hours=1), T0 + timedelta(hours=2)]


def test_duplicate_is_reported_and_dropped() -> None:
    series = [candle(0), candle(1), candle(1), candle(2)]
    assert check_candles(series, "1h").duplicates == [T0 + timedelta(hours=1)]
    assert [c.open_time for c in valid_candles(series, "1h")] == [
        T0,
        T0 + timedelta(hours=1),
        T0 + timedelta(hours=2),
    ]


def test_impossible_values_are_reported_and_dropped() -> None:
    bad = [
        candle(0, h="104"),  # high below the close
        candle(1, low="101"),  # low above the open
        candle(2, v="-1"),  # negative volume
        candle(3.5),  # not on an hour boundary
    ]
    report = check_candles(bad, "1h")
    assert [reason for _, reason in report.invalid] == [
        "high is below open/close",
        "low is above open/close",
        "negative volume",
        "open_time is not on a candle boundary",
    ]
    assert valid_candles(bad, "1h") == []


def test_four_hour_candles_must_open_on_four_hour_boundaries() -> None:
    assert check_candles([candle(0), candle(4)], "4h").ok
    assert not check_candles([candle(1)], "4h").ok
