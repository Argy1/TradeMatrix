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
