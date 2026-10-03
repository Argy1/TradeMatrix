"""Public /v1 endpoints: assets, candles with indicators, and status."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.errors import ApiError
from app.api.schemas import (
    AssetOut,
    CandleFreshness,
    CandleOut,
    CandlesResponse,
    JobStatus,
    ModelStatus,
    StatusResponse,
    price,
)
from app.data import repo
from app.features.chart import WARMUP, indicator_rows
from app.timeframes import TIMEFRAMES, Timeframe

router = APIRouter(prefix="/v1")


async def get_db() -> AsyncIterator[AsyncSession]:
    factory = db.session_factory()
    if factory is None:
        raise ApiError(503, "database_unavailable", "Database is not configured")
    async with factory() as session:
        yield session


Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("/assets", response_model=list[AssetOut], tags=["market"])
async def list_assets(session: Db) -> list[AssetOut]:
    """Supported coins."""
    return [
        AssetOut(symbol=a.symbol, name=a.name, exchange_symbol=a.exchange_symbol)
        for a in await repo.list_assets(session)
    ]


@router.get("/candles", response_model=CandlesResponse, tags=["market"])
async def get_candles(
    session: Db,
    symbol: str,
    tf: Timeframe,
    limit: Annotated[int, Query(ge=1, le=500)] = 500,
    before: datetime | None = None,
) -> CandlesResponse:
    """Closed candles (oldest first) with indicator series computed on the server."""
    asset = await repo.get_asset(session, symbol.upper())
    if asset is None:
        raise ApiError(404, "not_found", "Asset not found")
    if before is not None and before.tzinfo is None:
        before = before.replace(tzinfo=UTC)  # the API speaks UTC everywhere

    candles = await repo.fetch_candles(session, asset.id, tf, limit + WARMUP, before)
    # pandas work is CPU-bound, so it runs in a thread and does not block other requests.
    indicators = await asyncio.to_thread(indicator_rows, candles)
    latest = await repo.latest_open_time(session, asset.id, tf)

    shown = [
        CandleOut(
            t=c.open_time,
            o=price(c.open),
            h=price(c.high),
            l=price(c.low),
            c=price(c.close),
            v=price(c.volume),
            **values,
        )
        for c, values in zip(candles[-limit:], indicators[-limit:], strict=True)
    ]
    return CandlesResponse(
        symbol=asset.symbol,
        timeframe=tf,
        candles=shown,
        stale=repo.is_stale(latest, tf, datetime.now(UTC)),
    )


@router.get("/status", response_model=StatusResponse, tags=["ops"])
async def get_status(session: Db) -> StatusResponse:
    """When each job last succeeded and how fresh the stored candles are."""
    now = datetime.now(UTC)
    latest_by_timeframe = await repo.oldest_latest_candle(session)
    freshness = [
        CandleFreshness(
            timeframe=timeframe,
            latest_open_time=latest_by_timeframe[timeframe],
            stale=repo.is_stale(latest_by_timeframe[timeframe], timeframe, now),
        )
        for timeframe in TIMEFRAMES
    ]
    jobs = [
        JobStatus(
            job_name=h.job_name,
            last_run_at=h.last_run_at,
            last_success_at=h.last_success_at,
            last_error=h.last_error,
        )
        for h in await repo.list_heartbeats(session)
    ]
    models = [
        ModelStatus(
            symbol=symbol, timeframe=tf, model_version_id=mid, trained_at=trained, status=status
        )
        for symbol, tf, mid, trained, status in await repo.active_model_status(session)
    ]
    return StatusResponse(
        jobs=jobs, candles=freshness, models=models, stale=any(f.stale for f in freshness)
    )
