"""Worker service: runs the scheduled jobs. Start with: uv run python -m app.worker.main

Exactly ONE worker replica runs in production (docs/02). The advisory locks in jobs.py are a
second safety net in case two ever run at the same time.
"""

import asyncio
import contextlib
import logging
import signal
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app import db
from app.config import get_settings
from app.data.exchanges import get_exchange_client
from app.data.news import get_news_sources, news_http
from app.ml.predict import ModelCache
from app.ml.storage import ModelStorage
from app.observability import init_sentry
from app.sentiment.gemini import GeminiScorer
from app.timeframes import TIMEFRAMES
from app.worker.jobs import candle_close, heartbeat_work, log, news_job, run_job, sentiment_job


async def main() -> None:
    # stdout, not stderr: Railway shows stderr lines as errors.
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    settings = get_settings()
    init_sentry("worker")
    client = get_exchange_client(settings)
    storage = ModelStorage(
        settings.supabase_url, settings.supabase_service_role_key, settings.supabase_models_bucket
    )
    cache = ModelCache(storage)
    k = settings.sentiment_blend_k
    feeds = news_http()
    # Without a key the worker still runs everything else; headlines just stay unscored.
    scorer = None
    if settings.gemini_api_key and settings.gemini_model:
        scorer = GeminiScorer.from_key(settings.gemini_api_key, settings.gemini_model)

    # Catch up first: load every candle missed while the worker was down, predict the newest
    # candles (skipped if already done), and resolve finished predictions.
    await candle_close(client, cache, k, list(TIMEFRAMES))

    scheduler = AsyncIOScheduler(timezone="UTC")
    # 5 seconds after every full hour, when 1h (and sometimes 4h/1d) candles have just closed.
    scheduler.add_job(
        candle_close,
        CronTrigger(minute=0, second=5, timezone="UTC"),
        args=[client, cache, k],
        id="candle_close",
        max_instances=1,  # never two runs of the same job at once
        coalesce=True,  # after a pause, run once instead of once per missed hour
        misfire_grace_time=600,
    )
    # Headlines every 15 minutes, at :02 :17 :32 :47, so it never starts together with the
    # hourly candle run at :00.
    scheduler.add_job(
        run_job,
        CronTrigger(minute="2-59/15", timezone="UTC"),
        args=["ingest_news", news_job(get_news_sources(feeds))],
        id="ingest_news",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )
    if scorer is not None:
        # Two minutes after the headlines arrive: :04 :19 :34 :49.
        scheduler.add_job(
            run_job,
            CronTrigger(minute="4-59/15", timezone="UTC"),
            args=[
                "score_sentiment",
                sentiment_job(
                    scorer,
                    settings.sentiment_max_per_run,
                    settings.sentiment_batch_size,
                    settings.sentiment_max_per_day,
                ),
            ],
            id="score_sentiment",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
    else:
        log("sentiment_disabled", reason="GEMINI_API_KEY or GEMINI_MODEL is not set")
    scheduler.add_job(
        run_job,
        IntervalTrigger(minutes=5),
        args=["heartbeat", heartbeat_work],
        id="heartbeat",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    log("worker_started", jobs=[job.id for job in scheduler.get_jobs()])

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        # Railway sends SIGTERM on redeploy; finish cleanly. (Not available on Windows.)
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop.set)
    try:
        await stop.wait()
    finally:
        scheduler.shutdown(wait=False)
        await client.aclose()
        await storage.aclose()
        await feeds.aclose()
        if scorer is not None:
            await scorer.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
        log("worker_stopped")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
