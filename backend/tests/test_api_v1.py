"""Contract tests for /v1 with the database replaced by in-memory fakes."""

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api import v1
from app.api.main import app
from app.data.exchanges.base import Candle
from app.data.repo import Asset, Heartbeat
from app.features.chart import WARMUP
from app.timeframes import last_closed_open_time

BTC = Asset(id=1, symbol="BTC", name="Bitcoin", exchange_symbol="BTCUSDT")
NOW = datetime.now(UTC)
LAST_OPEN = last_closed_open_time(NOW, "1h")


def make_candles(count: int, last_open: datetime = LAST_OPEN) -> list[Candle]:
    candles = []
    for i in range(count):
        close = Decimal("60000") + Decimal(str(round(500 * math.sin(i / 9), 2)))
        candles.append(
            Candle(
                open_time=last_open - timedelta(hours=count - 1 - i),
                open=close - 10,
                high=close + 25,
                low=close - 30,
                close=close,
                volume=Decimal("12.50000000"),
            )
        )
    return candles


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    stored = make_candles(900)
    calls: dict = {}

    async def fake_db():
        yield None  # the fakes below never touch the session

    async def list_assets(_session):
        return [BTC]

    async def get_asset(_session, symbol):
        return BTC if symbol == "BTC" else None

    async def fetch_candles(_session, _asset_id, _timeframe, limit, before=None):
        calls["fetch"] = {"limit": limit, "before": before}
        rows = [c for c in stored if before is None or c.open_time < before]
        return rows[-limit:]

    async def latest_open_time(_session, _asset_id, _timeframe):
        return calls.get("latest", stored[-1].open_time)

    async def oldest_latest_candle(_session):
        return {"1h": stored[-1].open_time, "4h": None, "1d": None}

    async def list_heartbeats(_session):
        return [Heartbeat("ingest_candles", NOW, NOW, None)]

    async def active_model_status(_session):
        return [("BTC", "1h", 16, NOW, "ok"), ("SOL", "1h", 18, NOW, "degraded")]

    for name, fake in {
        "list_assets": list_assets,
        "get_asset": get_asset,
        "fetch_candles": fetch_candles,
        "latest_open_time": latest_open_time,
        "oldest_latest_candle": oldest_latest_candle,
        "list_heartbeats": list_heartbeats,
        "active_model_status": active_model_status,
    }.items():
        monkeypatch.setattr(v1.repo, name, fake)
    app.dependency_overrides[v1.get_db] = fake_db
    test_client = TestClient(app)
    test_client.calls = calls
    yield test_client
    app.dependency_overrides.clear()


def test_assets(client: TestClient) -> None:
    response = client.get("/v1/assets")
    assert response.status_code == 200
    assert response.json() == [{"symbol": "BTC", "name": "Bitcoin", "exchange_symbol": "BTCUSDT"}]


def test_candles_shape_and_warm_up(client: TestClient) -> None:
    response = client.get("/v1/candles", params={"symbol": "btc", "tf": "1h", "limit": 100})
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "BTC"
    assert body["timeframe"] == "1h"
    assert body["stale"] is False
    assert len(body["candles"]) == 100
    # Extra history is loaded so even the FIRST returned candle has every indicator.
    assert client.calls["fetch"]["limit"] == 100 + WARMUP
    first = body["candles"][0]
    assert all(first[name] is not None for name in ("ema50", "rsi14", "macd_signal", "bb_upper"))
    # Oldest first, one hour apart, UTC with a Z suffix.
    times = [c["t"] for c in body["candles"]]
    assert times == sorted(times)
    assert times[-1] == LAST_OPEN.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Prices are strings without float noise; indicators are numbers.
    last = body["candles"][-1]
    assert isinstance(last["c"], str) and Decimal(last["c"]) == make_candles(900)[-1].close
    assert last["v"] == "12.5"
    assert isinstance(last["ema9"], float)
    assert 0 <= last["rsi14"] <= 100
    assert last["bb_lower"] <= last["bb_mid"] <= last["bb_upper"]


def test_candles_without_enough_history_return_nulls(client: TestClient) -> None:
    before = (LAST_OPEN - timedelta(hours=889)).isoformat()  # only 10 candles are older
    body = client.get("/v1/candles", params={"symbol": "BTC", "tf": "1h", "before": before}).json()
    assert len(body["candles"]) == 10
    assert body["candles"][-1]["ema50"] is None
    assert body["candles"][-1]["ema9"] is not None


def test_candles_before_pages_backwards(client: TestClient) -> None:
    before = LAST_OPEN - timedelta(hours=10)
    body = client.get(
        "/v1/candles",
        params={"symbol": "BTC", "tf": "1h", "limit": 5, "before": before.isoformat()},
    ).json()
    assert body["candles"][-1]["t"] == (before - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_candles_marked_stale_when_the_latest_candle_is_missing(client: TestClient) -> None:
    client.calls["latest"] = LAST_OPEN - timedelta(hours=3)
    body = client.get("/v1/candles", params={"symbol": "BTC", "tf": "1h", "limit": 5}).json()
    assert body["stale"] is True


@pytest.mark.parametrize(
    ("params", "status", "code"),
    [
        ({"symbol": "NOTACOIN", "tf": "1h"}, 404, "not_found"),
        ({"symbol": "BTC", "tf": "5m"}, 422, "validation_error"),
        ({"symbol": "BTC", "tf": "1h", "limit": 501}, 422, "validation_error"),
        ({"symbol": "BTC", "tf": "1h", "limit": 0}, 422, "validation_error"),
        ({"tf": "1h"}, 422, "validation_error"),
    ],
)
def test_candles_errors(client: TestClient, params: dict, status: int, code: str) -> None:
    response = client.get("/v1/candles", params=params)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_status(client: TestClient) -> None:
    body = client.get("/v1/status").json()
    assert [j["job_name"] for j in body["jobs"]] == ["ingest_candles"]
    by_timeframe = {c["timeframe"]: c for c in body["candles"]}
    assert by_timeframe["1h"]["stale"] is False
    assert by_timeframe["4h"] == {"timeframe": "4h", "latest_open_time": None, "stale": True}
    assert body["stale"] is True  # one stale timeframe makes the whole status stale
    assert [(m["symbol"], m["status"]) for m in body["models"]] == [
        ("BTC", "ok"),
        ("SOL", "degraded"),
    ]


def test_database_not_configured_gives_503() -> None:
    response = TestClient(app).get("/v1/assets")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"
