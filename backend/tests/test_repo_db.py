"""SQL tests against the REAL database. Run on purpose with: uv run pytest -m db

Each test works inside a transaction that is rolled back, with candles dated in 2001, so
nothing is ever left behind and real data is never touched.
"""

import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import BACKEND_DIR, REPO_ROOT, Settings
from app.data import repo
from app.data.exchanges.base import Candle

pytestmark = pytest.mark.db
T0 = datetime(2001, 1, 1, tzinfo=UTC)


def candle(hours: int, close: str = "105.12345678") -> Candle:
    return Candle(
        T0 + timedelta(hours=hours), Decimal("100"), Decimal("110"), Decimal("90"),
        Decimal(close), Decimal("1.5"),
    )  # fmt: skip


@pytest.fixture
async def session():
    # conftest.py blanks DATABASE_URL for normal tests, so read the .env files directly here.
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
    async with engine.connect() as connection:
        transaction = await connection.begin()
        yield AsyncSession(bind=connection, expire_on_commit=False)
        await transaction.rollback()
    await engine.dispose()


async def test_seeded_assets(session: AsyncSession) -> None:
    assets = await repo.list_assets(session)
    assert [a.symbol for a in assets] == ["BTC", "ETH", "SOL", "BNB", "XRP"]
    assert (await repo.get_asset(session, "BTC")).exchange_symbol == "BTCUSDT"
    assert await repo.get_asset(session, "DOGE") is None


async def test_upsert_is_idempotent_and_exact(session: AsyncSession) -> None:
    btc = await repo.get_asset(session, "BTC")
    batch = [candle(i) for i in range(5)]

    await repo.upsert_candles(session, btc.id, "1h", batch)
    await repo.upsert_candles(session, btc.id, "1h", batch)  # the same candles again
    await repo.upsert_candles(session, btc.id, "1h", [candle(4, close="107")])  # a correction

    stored = await repo.fetch_candles(
        session, btc.id, "1h", limit=10, before=T0 + timedelta(days=1)
    )
    assert [c.open_time for c in stored] == [c.open_time for c in batch]  # 5 rows, oldest first
    assert stored[0].close == Decimal("105.12345678")  # numeric keeps every digit
    assert stored[-1].close == Decimal("107")  # the later value replaced the row


async def test_gap_detection(session: AsyncSession) -> None:
    eth = await repo.get_asset(session, "ETH")
    await repo.upsert_candles(session, eth.id, "1h", [candle(0), candle(1), candle(5)])
    gaps = [g for g in await repo.find_gaps(session, eth.id, "1h") if g[1] < T0 + timedelta(days=1)]
    assert gaps == [(T0 + timedelta(hours=1), T0 + timedelta(hours=5))]


async def test_heartbeat_keeps_the_last_success_after_a_failure(session: AsyncSession) -> None:
    await repo.record_heartbeat(session, "test_job")
    await repo.record_heartbeat(session, "test_job", error="boom")
    beat = next(h for h in await repo.list_heartbeats(session) if h.job_name == "test_job")
    assert beat.last_error == "boom"
    assert beat.last_success_at is not None
