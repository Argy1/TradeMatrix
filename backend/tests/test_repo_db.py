"""SQL tests against the REAL database. Run on purpose with: uv run pytest -m db

Each test works inside a transaction that is rolled back, with candles dated in 2001, so
nothing is ever left behind and real data is never touched.
"""

import json
import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import BACKEND_DIR, REPO_ROOT, Settings
from app.data import repo
from app.data.exchanges.base import Candle
from app.data.news.base import FeedError, Headline
from app.data.news.ingest import ingest_news, prune_old_news
from app.ml import snapshots

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
    symbols = [a.symbol for a in assets]
    assert symbols[:5] == ["BTC", "ETH", "SOL", "BNB", "XRP"]  # the original v1 coins first
    assert len(symbols) == len(set(symbols)) >= 5
    assert (await repo.get_asset(session, "BTC")).exchange_symbol == "BTCUSDT"
    assert await repo.get_asset(session, "NOTACOIN") is None


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


# ---- Compact feature snapshot (migration 20261007120000_compact_feature_snapshot) ----


def as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else json.loads(value)


async def snapshot_model(session: AsyncSession, names: list[str]) -> tuple[int, int]:
    """An inactive BTC 1h model version just for the test: (asset id, model version id)."""
    migrated = await session.execute(
        text(
            "select 1 from information_schema.columns where table_schema = 'public' "
            "and table_name = 'predictions' and column_name = 'feature_values'"
        )
    )
    if migrated.first() is None:
        pytest.skip("migration 20261007120000_compact_feature_snapshot is not applied yet")
    btc = await repo.get_asset(session, "BTC")
    model_id = await session.execute(
        text(
            "insert into model_versions (asset_id, timeframe, train_start, train_end, "
            "artifact_path, feature_names) "
            "values (:a, '1h', :t, :t, 'test/none.joblib', cast(:names as text[])) returning id"
        ),
        {"a": btc.id, "t": T0, "names": names},
    )
    return btc.id, model_id.scalar_one()


async def add_signal(
    session: AsyncSession,
    asset_id: int,
    model_id: int,
    hours: int,
    *,
    features: dict | None = None,
    values: list[float | None] | None = None,
) -> int:
    inserted = await session.execute(
        text(
            "insert into predictions (asset_id, timeframe, base_open_time, target_open_time, "
            "base_close, p_ml, p_up, label, model_version_id, features, feature_values) "
            "values (:a, '1h', :base, :target, 100, 0.6, 0.6, 'up', :m, "
            "cast(:features as jsonb), cast(:values as real[])) returning id"
        ),
        {
            "a": asset_id,
            "m": model_id,
            "base": T0 + timedelta(hours=hours),
            "target": T0 + timedelta(hours=hours + 1),
            "features": None if features is None else json.dumps(features),
            "values": values,
        },
    )
    return inserted.scalar_one()


async def stored_snapshot(session: AsyncSession, prediction_id: int) -> tuple:
    row = await session.execute(
        text("select features, feature_values from predictions where id = :id"),
        {"id": prediction_id},
    )
    return tuple(row.one())


async def test_compact_snapshot_reads_back_with_its_names(session: AsyncSession) -> None:
    asset_id, model_id = await snapshot_model(session, ["rsi14", "btc_ret_1", "ret_1"])
    compact = await add_signal(session, asset_id, model_id, 0, values=[61.5, None, -0.25])
    legacy = await add_signal(session, asset_id, model_id, 1, features={"rsi14": 40.0})

    rows = await session.execute(
        text(
            "select prediction_id, features from prediction_features "
            "where prediction_id = any(:ids)"
        ),
        {"ids": [compact, legacy]},
    )
    seen = {row.prediction_id: as_dict(row.features) for row in rows}
    # Names come from the model version, values from the signal; null keeps its place.
    assert seen[compact] == {"rsi14": 61.5, "btc_ret_1": None, "ret_1": -0.25}
    assert seen[legacy] == {"rsi14": 40.0}  # old rows still read from their JSON

    # A signal with no snapshot at all is refused: rule 7, every prediction is auditable.
    with pytest.raises(IntegrityError):
        async with session.begin_nested():  # savepoint, so the test transaction survives
            await add_signal(session, asset_id, model_id, 2)


async def test_old_json_snapshots_convert_and_are_checked(session: AsyncSession) -> None:
    asset_id, model_id = await snapshot_model(session, ["rsi14", "btc_ret_1", "ret_1"])
    old = await add_signal(
        session, asset_id, model_id, 0, features={"ret_1": -0.25, "rsi14": 61.5, "btc_ret_1": None}
    )
    # Different names than the model's: must be left alone, never squeezed into the list.
    other = await add_signal(session, asset_id, model_id, 1, features={"rsi14": 61.5})

    assert await snapshots.convert_json_rows(session, model_id) == 1
    assert await snapshots.convert_json_rows(session, model_id) == 0  # again: nothing to do
    assert (await stored_snapshot(session, old))[1] == [61.5, None, -0.25]  # the model's order
    assert (await stored_snapshot(session, other))[1] is None
    assert await snapshots.count_mismatches(session, model_id) == 0

    # The check must notice a value sitting under the wrong name.
    await session.execute(
        text("update predictions set feature_values = '{-0.25,null,61.5}' where id = :id"),
        {"id": old},
    )
    assert await snapshots.count_mismatches(session, model_id) == 1
    await session.execute(
        text("update predictions set feature_values = '{61.5,null,-0.25}' where id = :id"),
        {"id": old},
    )

    assert await snapshots.clear_json_rows(session, model_id) == 1
    assert (await stored_snapshot(session, old))[0] is None
    assert as_dict((await stored_snapshot(session, other))[0]) == {"rsi14": 61.5}


# ---- News ingestion ----


class FakeSource:
    def __init__(self, name: str, headlines: list[Headline] | None = None, error=None) -> None:
        self.name, self._headlines, self._error = name, headlines or [], error

    async def fetch(self) -> list[Headline]:
        if self._error:
            raise self._error
        return self._headlines


async def test_headlines_are_stored_once_and_tagged(session: AsyncSession) -> None:
    now = T0 + timedelta(days=150)
    site = "https://news.example.test"
    story = Headline(
        "feed-a", "Bitcoin and Solana rally on test news", f"{site}/a/1", now - timedelta(hours=2)
    )
    # The same story from a second source: other URL, other capitals and punctuation.
    copy = Headline(
        "feed-b", "BITCOIN and Solana rally, on test news!", f"{site}/b/9", now - timedelta(hours=1)
    )
    old = Headline("feed-a", "Something from last month", f"{site}/a/2", now - timedelta(days=30))
    ahead = Headline(
        "feed-a", "This source has a fast clock", f"{site}/a/3", now + timedelta(hours=5)
    )
    sources = [
        FakeSource("feed-a", [story, old, ahead]),
        FakeSource("feed-b", [copy]),
        FakeSource("down", error=FeedError("no answer")),
    ]

    first = await ingest_news(session, sources, now=now)
    again = await ingest_news(session, sources, now=now)  # the job running a second time

    assert (first["fetched"], first["stored"]) == (4, 2)
    assert again["stored"] == 0
    assert first["errors"] == ["down: FeedError: no answer"]  # reported, others still stored
    rows = await session.execute(
        text(
            "select source, url, published_at, asset_symbols from news_items "
            "where url like :site order by url"
        ),
        {"site": f"{site}/%"},
    )
    assert [tuple(row) for row in rows] == [
        ("feed-a", f"{site}/a/1", now - timedelta(hours=2), ["BTC", "SOL"]),
        ("feed-a", f"{site}/a/3", now, []),  # a time in the future is stored as "now"
    ]


async def test_old_headlines_are_pruned(session: AsyncSession) -> None:
    now = T0 + timedelta(days=150)
    await session.execute(
        text(
            "insert into news_items (source, title, url, title_hash, published_at) values "
            "('feed-a', 'Old', 'https://news.example.test/old', 'h-old', :old), "
            "('feed-a', 'Recent', 'https://news.example.test/recent', 'h-recent', :recent)"
        ),
        {"old": now - timedelta(days=91), "recent": now - timedelta(days=89)},
    )
    assert await prune_old_news(session, now) == 1
    left = await session.execute(
        text("select title from news_items where url like 'https://news.example.test/%'")
    )
    assert [row.title for row in left] == ["Recent"]
