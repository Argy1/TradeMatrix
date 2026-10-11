"""Fetch closed candles from the exchange and store them (the `ingest_candles` job logic)."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.exchanges.base import ExchangeClient
from app.data.quality import QualityReport, check_candles, valid_candles
from app.timeframes import TIMEFRAMES, floor_time, last_closed_open_time

# History to load the first time (docs/03): 1h about 2 years, 4h about 3, 1d about 5.
# The fast sizes only need what the live system uses: at least 1,500 candles for the chart and
# the features. Their long history for training lives in files (app/data/history.py).
BACKFILL_DAYS = {"1m": 2, "3m": 4, "5m": 6, "15m": 16, "30m": 32, "1h": 730, "4h": 1095, "1d": 1826}


FETCH_PARALLEL = 8  # requests to the exchange at the same time
RETRY_AFTER = 1.0  # seconds to wait when the candle that just closed is not served yet


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
    commit: bool = True,
) -> IngestResult:
    """Store every closed candle we do not have yet for one asset and timeframe.

    Idempotent and resumable: it continues after the newest stored candle, and the upsert
    means a repeated or interrupted run can never create duplicates. The worker passes
    commit=False because it commits once, at the end of the whole job.
    """
    now = now or datetime.now(UTC)
    latest = await repo.latest_open_time(session, asset.id, timeframe)
    start = first_missing(latest, timeframe, now)
    candles = await client.get_klines(asset.exchange_symbol, timeframe, start=start)
    return await _store(session, asset, timeframe, candles, commit=commit)


def first_missing(latest: datetime | None, timeframe: str, now: datetime) -> datetime:
    """Open time of the first candle we do not have yet."""
    if latest is None:
        return floor_time(now - timedelta(days=BACKFILL_DAYS[timeframe]), timeframe)
    return latest + TIMEFRAMES[timeframe]


async def ingest_many(
    session: AsyncSession,
    client: ExchangeClient,
    assets: Sequence[repo.Asset],
    timeframes: Sequence[str],
    *,
    now: datetime | None = None,
    sleep=asyncio.sleep,
) -> dict:
    """`ingest_candles` for many coins and sizes: the exchange is asked for all of them at the
    same time (the slow part is waiting for answers), then everything is stored in order.

    One coin that fails does not stop the others; its error is returned in "errors".
    If the candle that just closed is not served yet, that request is repeated once after a
    second: a signal one second late is better than no signal for that minute.
    """
    now = now or datetime.now(UTC)
    latest = await repo.latest_open_times(session, timeframes)
    gate = asyncio.Semaphore(FETCH_PARALLEL)
    retried = 0

    async def fetch(asset: repo.Asset, timeframe: str) -> list:
        nonlocal retried
        newest_closed = last_closed_open_time(now, timeframe)
        start = first_missing(latest.get((asset.id, timeframe)), timeframe, now)
        if start > newest_closed:
            return []  # already up to date
        async with gate:
            candles = await client.get_klines(asset.exchange_symbol, timeframe, start=start)
            if not candles or candles[-1].open_time < newest_closed:
                retried += 1
                await sleep(RETRY_AFTER)
                candles = await client.get_klines(asset.exchange_symbol, timeframe, start=start)
        return candles

    pairs = [(asset, timeframe) for asset in assets for timeframe in timeframes]
    answers = await asyncio.gather(*(fetch(a, tf) for a, tf in pairs), return_exceptions=True)
    batches, errors = [], []
    for (asset, timeframe), answer in zip(pairs, answers, strict=True):
        if isinstance(answer, BaseException):
            errors.append(f"{asset.symbol} {timeframe}: {type(answer).__name__}: {answer}")
        elif answer:
            batches.append((asset.id, timeframe, valid_candles(answer, timeframe)))
    stored = await repo.upsert_many(session, batches)  # one trip to the database for all coins
    return {
        "timeframes": list(timeframes),
        "stored": stored,
        "retried": retried,
        "errors": errors,
    }


async def extend_history(
    session: AsyncSession,
    client: ExchangeClient,
    asset: repo.Asset,
    timeframe: str,
    since: datetime,
) -> IngestResult:
    """Load candles older than the oldest stored one, back to `since` (more training data)."""
    earliest = await repo.earliest_open_time(session, asset.id, timeframe)
    since = floor_time(since, timeframe)
    if earliest is None or since >= earliest:
        return IngestResult(asset.symbol, timeframe, 0, 0, check_candles([], timeframe))
    end = earliest - TIMEFRAMES[timeframe]
    candles = await client.get_klines(asset.exchange_symbol, timeframe, start=since, end=end)
    return await _store(session, asset, timeframe, candles)


async def _store(
    session: AsyncSession,
    asset: repo.Asset,
    timeframe: str,
    candles: list,
    *,
    commit: bool = True,
) -> IngestResult:
    quality = check_candles(candles, timeframe)
    stored = await repo.upsert_candles(
        session, asset.id, timeframe, valid_candles(candles, timeframe)
    )
    if commit:
        await session.commit()
    return IngestResult(asset.symbol, timeframe, len(candles), stored, quality)
