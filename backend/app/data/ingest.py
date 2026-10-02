"""Fetch closed candles from the exchange and store them (the `ingest_candles` job logic)."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.exchanges.base import ExchangeClient
from app.data.quality import QualityReport, check_candles, valid_candles
from app.timeframes import TIMEFRAMES, floor_time

# History to load the first time (docs/03): 1h about 2 years, 4h about 3, 1d about 5.
BACKFILL_DAYS = {"1h": 730, "4h": 1095, "1d": 1826}


@dataclass
class IngestResult:
    symbol: str
    timeframe: str
    fetched: int
    stored: int
    quality: QualityReport


async def ingest_candles(
    session: AsyncSession,
    client: ExchangeClient,
    asset: repo.Asset,
    timeframe: str,
    *,
    now: datetime | None = None,
) -> IngestResult:
    """Store every closed candle we do not have yet for one asset and timeframe.

    Idempotent and resumable: it continues after the newest stored candle, and the upsert
    means a repeated or interrupted run can never create duplicates.
    """
    now = now or datetime.now(UTC)
    latest = await repo.latest_open_time(session, asset.id, timeframe)
    if latest is None:
        start = floor_time(now - timedelta(days=BACKFILL_DAYS[timeframe]), timeframe)
    else:
        start = latest + TIMEFRAMES[timeframe]

    candles = await client.get_klines(asset.exchange_symbol, timeframe, start=start)
    quality = check_candles(candles, timeframe)
    stored = await repo.upsert_candles(
        session, asset.id, timeframe, valid_candles(candles, timeframe)
    )
    await session.commit()
    return IngestResult(asset.symbol, timeframe, len(candles), stored, quality)
