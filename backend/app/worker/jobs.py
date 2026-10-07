"""Worker jobs. Each run is one database transaction guarded by an advisory lock."""

import json
import logging
import time
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.alerts.evaluate import evaluate_price_alerts, evaluate_signal_alerts
from app.data import repo
from app.data.exchanges import ExchangeClient
from app.data.ingest import ingest_candles
from app.data.news import NewsSource
from app.data.news.ingest import ingest_news
from app.ml.predict import ModelCache, resolve_outcomes, run_predictions
from app.sentiment.score import Scorer, score_sentiment
from app.timeframes import TIMEFRAMES, floor_time

logger = logging.getLogger("worker")


def log(event: str, **fields: object) -> None:
    """One JSON object per line: easy to search in Railway's log viewer."""
    logger.info(json.dumps({"event": event, **fields}, default=str))


def closed_timeframes(now: datetime) -> list[str]:
    """Timeframes whose candle closed at the start of this hour (1h always, 4h every 4 hours,
    1d at 00:00 UTC)."""
    hour_start = floor_time(now, "1h")
    return [tf for tf in TIMEFRAMES if floor_time(hour_start, tf) == hour_start]


async def try_lock(session: AsyncSession, job_name: str) -> bool:
    """Postgres advisory lock for the current transaction.

    If a second worker ever runs by mistake, it gets False and skips the job instead of doing
    the same work twice. The lock is released automatically when the transaction ends, which
    also works through Supabase's transaction pooler.
    """
    result = await session.execute(
        text("select pg_try_advisory_xact_lock(hashtext(:job))"), {"job": job_name}
    )
    return bool(result.scalar_one())


async def run_job(
    job_name: str, work: Callable[[AsyncSession], Awaitable[dict]], *, quiet_when_idle: bool = False
) -> None:
    """Run one job: lock, work, commit, then record the outcome in worker_heartbeat.

    `quiet_when_idle` is for the every-minute job: a run that had nothing to check writes no
    log line (1,440 identical lines a day would bury the useful ones). Errors are always logged.
    """
    factory = db.session_factory()
    if factory is None:
        log("job_skipped", job=job_name, reason="database not configured")
        return
    started = time.monotonic()
    error: str | None = None
    details: dict = {}
    async with factory() as session:
        try:
            async with session.begin():
                if not await try_lock(session, job_name):
                    log("job_skipped", job=job_name, reason="locked by another worker")
                    return
                details = await work(session)
        except Exception as exc:  # a failing job must never stop the scheduler
            error = f"{type(exc).__name__}: {exc}"[:500]
        # Partial failures (e.g. one model out of 15) are committed work plus a recorded error.
        if error is None and details.get("errors"):
            error = "; ".join(details["errors"])[:500]
        async with session.begin():
            await repo.record_heartbeat(session, job_name, error)
    if quiet_when_idle and error is None and not details.get("checked"):
        return
    log(
        "job_finished",
        job=job_name,
        ok=error is None,
        error=error,
        duration_ms=round((time.monotonic() - started) * 1000),
        **details,
    )


def ingest_job(client: ExchangeClient, timeframes: list[str] | None = None):
    """Fetch the candles that just closed for every active coin (all missed ones too)."""

    async def work(session: AsyncSession) -> dict:
        frames = timeframes or closed_timeframes(datetime.now(UTC))
        stored = 0
        for asset in await repo.list_assets(session):
            for timeframe in frames:
                result = await ingest_candles(session, client, asset, timeframe, commit=False)
                stored += result.stored
        return {"timeframes": frames, "stored": stored}

    return work


async def heartbeat_work(_session: AsyncSession) -> dict:
    return {}


def predictions_job(cache: ModelCache, blend_k: float, timeframes: list[str] | None = None):
    async def work(session: AsyncSession) -> dict:
        now = datetime.now(UTC)
        return await run_predictions(
            session, cache, timeframes or closed_timeframes(now), now, blend_k=blend_k
        )

    return work


async def outcomes_work(session: AsyncSession) -> dict:
    return await resolve_outcomes(session)


def news_job(sources: Sequence[NewsSource]):
    """Fetch headlines from every source and store the new ones (every 15 minutes)."""

    async def work(session: AsyncSession) -> dict:
        return await ingest_news(session, sources)

    return work


def sentiment_job(scorer: Scorer, max_per_run: int, batch_size: int, max_per_day: int):
    """Score new headlines with Gemini (every 15 minutes, shortly after `ingest_news`)."""
    tries: dict[int, int] = {}  # failed attempts per headline, kept while the worker runs

    async def work(session: AsyncSession) -> dict:
        details = await score_sentiment(
            session,
            scorer,
            max_per_run=max_per_run,
            batch_size=batch_size,
            max_per_day=max_per_day,
            tries=tries,
        )
        if details["budget_reached"]:
            log("sentiment_budget_reached", max_per_day=max_per_day)
        return details

    return work


async def alerts_work(session: AsyncSession) -> dict:
    """Signal alerts, checked against the predictions that were just stored."""
    return await evaluate_signal_alerts(session)


def price_alerts_job(client: ExchangeClient):
    """Price alerts, every minute. Prices from the previous check stay in memory: a crossing
    needs two prices, and after a restart the first check only sets the starting point."""
    last_prices: dict[str, Decimal] = {}

    async def work(session: AsyncSession) -> dict:
        return await evaluate_price_alerts(session, client, last_prices)

    return work


async def candle_close(
    client: ExchangeClient,
    cache: ModelCache,
    blend_k: float,
    timeframes: list[str] | None = None,
) -> None:
    """The heart of the system (docs/02): store the closed candles, predict the next ones,
    score the predictions whose target candle just closed, then check the signal alerts.
    In this order, every hour."""
    await run_job("ingest_candles", ingest_job(client, timeframes))
    await run_job("run_predictions", predictions_job(cache, blend_k, timeframes))
    await run_job("resolve_outcomes", outcomes_work)
    await run_job("evaluate_alerts", alerts_work)
