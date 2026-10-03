"""Signal endpoints: error contract with fakes, and real-data shape checks (marked db)."""

import os
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api import signals, v1
from app.api.main import app
from app.config import BACKEND_DIR, REPO_ROOT, Settings


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch):
    async def fake_db():
        yield None

    async def no_asset(_session, _symbol):
        return None

    monkeypatch.setattr(signals.repo, "get_asset", no_asset)
    app.dependency_overrides[v1.get_db] = fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/v1/predictions/latest?symbol=NOTACOIN&tf=1h", 404),
        ("/v1/predictions/history?symbol=NOTACOIN&tf=1h", 404),
        ("/v1/performance?symbol=NOTACOIN", 404),
        ("/v1/predictions/latest?symbol=BTC&tf=15m", 422),
        ("/v1/predictions/history?symbol=BTC&tf=1h&limit=501", 422),
        ("/v1/performance?days=0", 422),
    ],
)
def test_errors_use_the_shared_shape(fake_client: TestClient, path: str, status: int) -> None:
    response = fake_client.get(path)
    assert response.status_code == status
    assert set(response.json()["error"]) == {"code", "message"}


def test_staleness_rule() -> None:
    now = datetime(2026, 10, 3, 14, 10, tzinfo=UTC)
    fresh_target = datetime(2026, 10, 3, 14, 0, tzinfo=UTC)  # predicted at 14:00:05 for 14:00
    assert not signals.prediction_is_stale(fresh_target, "1h", now)
    assert signals.prediction_is_stale(fresh_target - timedelta(hours=1), "1h", now)
    # Just after a close, the next prediction is not expected yet (grace period).
    assert not signals.prediction_is_stale(fresh_target, "1h", now.replace(hour=15, minute=1))


@pytest.fixture
def real_client():
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
            yield session  # read-only: these endpoints never write

    app.dependency_overrides[v1.get_db] = real_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.db
def test_real_signal_endpoints(real_client: TestClient) -> None:
    latest = real_client.get("/v1/predictions/latest?symbol=BTC&tf=1h").json()
    assert latest["label"] in {"up", "down", "neutral"}
    assert 0 < latest["p_up"] < 1 and len(latest["reasons"]) == 3
    assert latest["model"]["status"] in {"ok", "degraded"}
    assert latest["disclaimer"].startswith("Signals are probabilistic estimates")
    assert {"model", "naive_baseline", "n", "low_sample"} <= set(latest["recent_accuracy"])

    history = real_client.get("/v1/predictions/history?symbol=BTC&tf=1h&limit=5").json()
    assert (
        history["items"] and history["items"][0]["target_open_time"] == latest["target_open_time"]
    )

    markets = real_client.get("/v1/markets").json()
    assert [m["symbol"] for m in markets][:5] == ["BTC", "ETH", "SOL", "BNB", "XRP"]
    assert set(markets[0]["signals"]) == {"1h", "4h", "1d"}
    assert markets[0]["last_price"] and markets[0]["change_24h_pct"] is not None

    summary = real_client.get("/v1/performance/summary?days=30").json()
    assert len(summary["rows"]) == 3 * len(markets)  # every coin x 1h/4h/1d, in one response
    assert summary["overall"]["n_predictions"] == sum(r["n_predictions"] for r in summary["rows"])

    perf = real_client.get("/v1/performance?days=30").json()
    assert perf["n_predictions"] >= 15
    assert "naive" in perf["baseline"] and perf["low_sample"] is True
