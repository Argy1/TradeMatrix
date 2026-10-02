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
from app.timeframes import TIMEFRAMES
from app.worker.jobs import heartbeat_work, ingest_job, log, run_job


async def main() -> None:
    # stdout, not stderr: Railway shows stderr lines as errors.
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    client = get_exchange_client(get_settings())

    # Catch up first: if the worker was down, this loads every candle it missed.
    await run_job("ingest_candles", ingest_job(client, list(TIMEFRAMES)))

    scheduler = AsyncIOScheduler(timezone="UTC")
    # 5 seconds after every full hour, when 1h (and sometimes 4h/1d) candles have just closed.
    scheduler.add_job(
        run_job,
        CronTrigger(minute=0, second=5, timezone="UTC"),
        args=["ingest_candles", ingest_job(client)],
        id="ingest_candles",
        max_instances=1,  # never two runs of the same job at once
        coalesce=True,  # after a pause, run once instead of once per missed hour
        misfire_grace_time=600,
    )
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
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
        log("worker_stopped")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
