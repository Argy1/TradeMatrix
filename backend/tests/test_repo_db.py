"""SQL tests against the REAL database. Run on purpose with: uv run pytest -m db

Each test works inside a transaction that is rolled back (the `session` fixture in
conftest.py), with candles dated in 2001, so nothing is ever left behind and real data is
never touched.
"""

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.exchanges.base import Candle
from app.data.news.base import FeedError, Headline
from app.data.news.ingest import ingest_news, prune_old_news, store_headlines
from app.features.build import build_dataset, feature_columns
from app.ml import snapshots
from app.ml.config import XGB_PARAMS
from app.ml.predict import run_predictions
from app.ml.registry import ModelBundle
from app.ml.train import fit_calibrated
from app.sentiment.aggregate import sentiment_by_asset
from app.sentiment.schemas import HeadlineSentiment
from app.sentiment.score import score_sentiment, scored_today
from app.timeframes import last_closed_open_time

pytestmark = pytest.mark.db
T0 = datetime(2001, 1, 1, tzinfo=UTC)


def candle(hours: int, close: str = "105.12345678") -> Candle:
    return Candle(
        T0 + timedelta(hours=hours), Decimal("100"), Decimal("110"), Decimal("90"),
        Decimal(close), Decimal("1.5"),
    )  # fmt: skip


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


async def require_snapshot_migration(session: AsyncSession) -> None:
    migrated = await session.execute(
        text(
            "select 1 from information_schema.columns where table_schema = 'public' "
            "and table_name = 'predictions' and column_name = 'feature_values'"
        )
    )
    if migrated.first() is None:
        pytest.skip("migration 20261007120000_compact_feature_snapshot is not applied yet")


async def snapshot_model(session: AsyncSession, names: list[str]) -> tuple[int, int]:
    """An inactive BTC 1h model version just for the test: (asset id, model version id)."""
    await require_snapshot_migration(session)
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


# ---- Sentiment ----


class TitleScorer:
    """Stands in for Gemini: answers headlines about Bitcoin, stays silent on the others."""

    model, prompt_version = "fake-model", "v-test"

    def __init__(self) -> None:
        self.batches: list[list[str]] = []

    async def score(self, headlines: list, symbols: list[str]) -> list[HeadlineSentiment]:
        self.batches.append([h.title for h in headlines])
        return [
            HeadlineSentiment(
                id=h.id, assets=["BTC"], score=0.5, confidence=0.25, event_type="market", reason="t"
            )
            for h in headlines
            if "Bitcoin" in h.title
        ]


async def test_headlines_are_scored_once_within_the_budget(session: AsyncSession) -> None:
    now = T0 + timedelta(days=150, hours=12)
    site = "https://news.example.test"
    headlines = [
        Headline("feed-a", "Bitcoin test headline", f"{site}/s/1", now - timedelta(hours=2)),
        Headline("feed-a", "The model never answers this", f"{site}/s/2", now - timedelta(hours=3)),
        Headline("feed-a", "Bitcoin news from yesterday", f"{site}/s/3", now - timedelta(hours=30)),
    ]
    assert await store_headlines(session, headlines, ["BTC", "ETH"], now) == 3
    scorer, tries = TitleScorer(), {}

    async def run(max_per_day: int = 100) -> dict:
        return await score_sentiment(
            session, scorer, max_per_run=10, batch_size=1, max_per_day=max_per_day, now=now,
            tries=tries,
        )  # fmt: skip

    first = await run()
    assert (first["scored"], first["requests"], first["waiting"]) == (1, 2, 1)
    # Newest first, and the 30-hour-old headline is never sent: it cannot change a signal.
    assert scorer.batches == [["Bitcoin test headline"], ["The model never answers this"]]

    second = await run()
    assert (second["scored"], second["requests"]) == (0, 1)  # the scored one is not sent again
    await run()
    assert (await run())["requests"] == 0  # after 3 silent tries the other one is left alone

    stored = await session.execute(
        text(
            "select s.assets, s.score, s.confidence, s.event_type, s.model, s.prompt_version "
            "from sentiments s join news_items n on n.id = s.news_id where n.url like :site"
        ),
        {"site": f"{site}/%"},
    )
    assert [tuple(row) for row in stored] == [
        (["BTC"], 0.5, 0.25, "market", "fake-model", "v-test")
    ]

    # One number per coin, and only from headlines that existed at that moment.
    assert await sentiment_by_asset(session, ["BTC", "ETH"], now) == {"BTC": 0.125, "ETH": 0.0}
    earlier = await sentiment_by_asset(session, ["BTC"], now - timedelta(hours=3))
    assert earlier == {"BTC": 0.0}

    # Daily budget: counted from the table (here: pretend the row was scored on this test day).
    await session.execute(
        text(
            "update sentiments set created_at = :now "
            "where news_id in (select id from news_items where url like :site)"
        ),
        {"now": now, "site": f"{site}/%"},
    )
    assert await scored_today(session, now) == 1
    capped = await run(max_per_day=1)
    assert capped["budget_reached"] and capped["requests"] == 0


class OneModelCache:
    def __init__(self, bundle: ModelBundle) -> None:
        self._bundle = bundle

    async def get(self, path: str) -> ModelBundle:
        return self._bundle


def small_bundle() -> ModelBundle:
    """A tiny model on made-up candles: enough to run the real prediction job's SQL."""
    rng = np.random.default_rng(5)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 1500)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    frame = pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * 1.002,
            "low": np.minimum(open_, close) * 0.998,
            "close": close,
            "volume": rng.uniform(10, 1000, 1500),
        },
        index=pd.date_range("2025-01-01", periods=1500, freq="h", tz="UTC"),
    )
    data = build_dataset(frame)
    params = XGB_PARAMS | {"n_estimators": 20, "early_stopping_rounds": 5}
    model = fit_calibrated(
        data.iloc[:900], data.iloc[900:1100], data.iloc[1100:1400], feature_columns(data), params
    )
    return ModelBundle(model, "BTC", "1h", "test", data.index[0], data.index[899])


async def test_prediction_job_stores_sentiment_and_both_snapshot_forms(
    session: AsyncSession,
) -> None:
    """The real `run_predictions` against the real tables, rolled back.

    The live worker has already written this hour's signals, so inside this transaction the
    rows of two coins are removed first (the rollback puts them back). The job then has to
    store them again: BTC in the compact form, ETH as JSON."""
    await require_snapshot_migration(session)
    bundle = small_bundle()
    names = list(bundle.model.features)
    # BTC's model gets stored names (compact form); every other coin has none here (JSON form).
    await session.execute(
        text(
            "update model_versions set feature_names = case when asset_id = "
            "(select id from assets where symbol = 'BTC') then cast(:names as text[]) end "
            "where is_active and timeframe = '1h'"
        ),
        {"names": names},
    )
    now = datetime.now(UTC)
    target = last_closed_open_time(now, "1h") + timedelta(hours=1)
    removed = await session.execute(
        text(
            "delete from predictions where timeframe = '1h' and target_open_time = :target "
            "and asset_id in (select id from assets where symbol in ('BTC', 'ETH'))"
        ),
        {"target": target},
    )

    result = await run_predictions(session, OneModelCache(bundle), ["1h"], now)

    assert result["errors"] == []  # every statement of the job was accepted by the database
    if removed.rowcount < 2:
        pytest.skip("the live worker has not stored this hour's signals yet: run it again")
    assert result["created"] == 2
    rows = await session.execute(
        text(
            "select a.symbol, p.features, p.feature_values, p.sentiment_agg, p.sentiment_k, "
            "v.features as through_view "
            "from predictions p join assets a on a.id = p.asset_id "
            "join prediction_features v on v.prediction_id = p.id "
            "where p.timeframe = '1h' and p.target_open_time = :target "
            "and a.symbol in ('BTC', 'ETH') order by a.symbol"
        ),
        {"target": target},
    )
    btc, eth = rows.all()
    # BTC: values only, in the model's order; the view puts the names back.
    assert btc.features is None and len(btc.feature_values) == len(names)
    assert set(as_dict(btc.through_view)) == set(names)  # (jsonb keeps its own key order)
    # The view prints 15 digits, the array holds the 4-byte number: the same value at the
    # precision that is stored (and that the model reads).
    shown, stored = as_dict(btc.through_view)["rsi14"], btc.feature_values[names.index("rsi14")]
    assert np.float32(shown) == np.float32(stored)
    # ETH: no stored names for its model, so the job kept the self-describing JSON.
    assert eth.feature_values is None and set(as_dict(eth.features)) == set(names)
    for row in (btc, eth):
        assert -1 <= row.sentiment_agg <= 1 and row.sentiment_k == 0  # stored, not blended
