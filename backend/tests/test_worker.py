import os
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import BACKEND_DIR, REPO_ROOT, Settings
from app.worker.jobs import closed_timeframes, try_lock


def test_closed_timeframes_follow_the_candle_boundaries() -> None:
    assert closed_timeframes(datetime(2026, 10, 3, 13, 0, 5, tzinfo=UTC)) == ["1h"]
    assert closed_timeframes(datetime(2026, 10, 3, 16, 0, 5, tzinfo=UTC)) == ["1h", "4h"]
    assert closed_timeframes(datetime(2026, 10, 3, 0, 0, 5, tzinfo=UTC)) == ["1h", "4h", "1d"]
    # A late run in the same hour still knows which candles closed at the hour's start.
    assert closed_timeframes(datetime(2026, 10, 3, 8, 9, 0, tzinfo=UTC)) == ["1h", "4h"]


@pytest.mark.db
async def test_advisory_lock_blocks_a_second_worker() -> None:
    """Two connections = two workers. While the first holds the lock, the second must skip."""
    os.environ.pop("DATABASE_URL", None)
    settings = Settings(_env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"))
    os.environ["DATABASE_URL"] = ""
    if not settings.database_configured:
        pytest.skip("DATABASE_URL is not configured")
    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )
    try:
        async with engine.connect() as first, engine.connect() as second:
            worker_a, worker_b = AsyncSession(bind=first), AsyncSession(bind=second)
            async with first.begin():
                assert await try_lock(worker_a, "test_lock_job")
                async with second.begin():
                    assert not await try_lock(worker_b, "test_lock_job")
            # The first transaction ended, so the lock is free again.
            async with second.begin():
                assert await try_lock(worker_b, "test_lock_job")
    finally:
        await engine.dispose()


def test_scheduler_has_every_job_at_its_time() -> None:
    """The wiring of the worker: a wrong name, time or argument here is a production outage,
    so it is checked without starting anything."""
    from apscheduler.triggers.cron import CronTrigger

    from app.config import Settings
    from app.worker.main import build_scheduler

    settings = Settings(_env_file=None)
    scheduler = build_scheduler(settings, client=None, cache=None, sources=[], scorer=object())
    jobs = {job.id: job for job in scheduler.get_jobs()}
    assert set(jobs) == {
        "candle_close", "ingest_news", "score_sentiment", "check_price_alerts", "heartbeat",
    }  # fmt: skip

    def fires(job_id: str, count: int) -> list[str]:
        """The next `count` times a job runs after 12:00:00 UTC, as HH:MM:SS."""
        trigger, moment, times = jobs[job_id].trigger, datetime(2026, 10, 9, 12, tzinfo=UTC), []
        assert isinstance(trigger, CronTrigger)
        for _ in range(count):
            moment = trigger.get_next_fire_time(moment, moment)
            times.append(f"{moment:%H:%M:%S}")
        return times

    assert fires("candle_close", 2) == ["12:00:05", "13:00:05"]  # 5 s after each hourly close
    assert fires("ingest_news", 5) == ["12:02:00", "12:17:00", "12:32:00", "12:47:00", "13:02:00"]
    assert fires("score_sentiment", 4) == ["12:04:00", "12:19:00", "12:34:00", "12:49:00"]
    assert fires("check_price_alerts", 2) == ["12:00:30", "12:01:30"]  # every minute
    assert jobs["check_price_alerts"].kwargs == {"quiet_when_idle": True}
    assert jobs["score_sentiment"].args[0] == "score_sentiment"

    # No Gemini key: everything else still runs, only the scoring job is left out.
    without = build_scheduler(settings, client=None, cache=None, sources=[], scorer=None)
    assert {job.id for job in without.get_jobs()} == set(jobs) - {"score_sentiment"}
