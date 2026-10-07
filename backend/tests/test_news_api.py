"""GET /v1/news: the response shape, the coin filter, and the error contract."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import news, v1
from app.api.main import app
from app.data import repo
from app.data.news import RSS_FEEDS, SOURCE_NAMES

ROWS = [
    SimpleNamespace(
        id=2, source="coindesk", title="Bitcoin ETF inflows continue",
        url="https://news.example.test/2", published_at=datetime(2026, 10, 7, 4, 0, tzinfo=UTC),
        symbols=["BTC"], score=0.3149, confidence=0.704, event_type="etf", reason="ETF inflows",
    ),
    SimpleNamespace(
        id=1, source="unknown-feed", title="A headline that is not scored yet",
        url="https://news.example.test/1", published_at=datetime(2026, 10, 7, 3, 0, tzinfo=UTC),
        symbols=[], score=None, confidence=None, event_type=None, reason=None,
    ),
]  # fmt: skip


class FakeSession:
    def __init__(self) -> None:
        self.params: dict = {}

    async def execute(self, _statement, params: dict):
        self.params = params
        return ROWS


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    session = FakeSession()

    async def fake_db():
        yield session

    async def get_asset(_session, symbol: str):
        return repo.Asset(1, "BTC", "Bitcoin", "BTCUSDT") if symbol == "BTC" else None

    monkeypatch.setattr(news.repo, "get_asset", get_asset)
    app.dependency_overrides[v1.get_db] = fake_db
    yield TestClient(app), session
    app.dependency_overrides.clear()


def test_news_items_carry_source_link_and_sentiment(client) -> None:
    http, session = client
    body = http.get("/v1/news?symbol=btc&limit=5").json()
    assert session.params == {"symbol": "BTC", "limit": 5}  # symbol is case-insensitive
    assert body["symbol"] == "BTC"
    scored, waiting = body["items"]
    assert scored == {
        "id": 2,
        "source": "coindesk",
        "source_name": "CoinDesk",
        "title": "Bitcoin ETF inflows continue",
        "url": "https://news.example.test/2",
        "published_at": "2026-10-07T04:00:00Z",
        "symbols": ["BTC"],
        "sentiment": {
            "label": "bullish",
            "score": 0.31,
            "confidence": 0.7,
            "event_type": "etf",
            "reason": "ETF inflows",
        },
    }
    # Not scored yet: no badge, and an unknown source falls back to its plain name.
    assert waiting["sentiment"] is None and waiting["source_name"] == "unknown-feed"


def test_all_news_without_a_symbol(client) -> None:
    http, session = client
    assert http.get("/v1/news").json()["symbol"] is None
    assert session.params == {"symbol": None, "limit": 30}


@pytest.mark.parametrize(
    ("path", "status"),
    [("/v1/news?symbol=NOTACOIN", 404), ("/v1/news?limit=0", 422), ("/v1/news?limit=101", 422)],
)
def test_news_errors_use_the_shared_shape(client, path: str, status: int) -> None:
    response = client[0].get(path)
    assert response.status_code == status
    assert set(response.json()["error"]) == {"code", "message"}


@pytest.mark.parametrize(
    ("score", "label"),
    [
        (0.31, "bullish"),
        (0.1, "bullish"),
        (0.02, "neutral"),
        (-0.09, "neutral"),
        (-0.22, "bearish"),
    ],
)
def test_badge_label_comes_from_the_server(score: float, label: str) -> None:
    assert news.sentiment_label(score) == label


def test_every_feed_has_a_display_name() -> None:
    assert set(SOURCE_NAMES) == set(RSS_FEEDS)


@pytest.mark.db
def test_news_query_runs_on_the_real_database() -> None:
    """Read-only: the real SQL with and without the coin filter, on the real tables."""
    import os

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from app.config import BACKEND_DIR, REPO_ROOT, Settings

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
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def real_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[v1.get_db] = real_db
    try:
        with TestClient(app) as http:
            everything = http.get("/v1/news?limit=5")
            one_coin = http.get("/v1/news?symbol=BTC&limit=5")
            unknown = http.get("/v1/news?symbol=NOTACOIN")
    finally:
        app.dependency_overrides.clear()
    assert everything.status_code == one_coin.status_code == 200 and unknown.status_code == 404
    assert one_coin.json()["symbol"] == "BTC" and len(everything.json()["items"]) <= 5
    for entry in everything.json()["items"]:
        assert entry["url"].startswith("http") and entry["source_name"]
