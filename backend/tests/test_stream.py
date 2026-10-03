"""Live stream: Binance message parsing, fan-out filtering and the WebSocket contract."""

import json

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.main import app
from app.api.stream import Client, hub, parse_kline

PAIRS = {"BTCUSDT": "BTC", "ETHUSDT": "ETH"}


def kline(symbol: str = "BTCUSDT", interval: str = "1h", closed: bool = False) -> str:
    return json.dumps(
        {
            "stream": f"{symbol.lower()}@kline_{interval}",
            "data": {
                "e": "kline",
                "k": {
                    "t": 1790978400000, "s": symbol, "i": interval, "o": "84531.68",
                    "h": "84600.00", "l": "84500.10", "c": "84588.00", "v": "412.3", "x": closed,
                },
            },
        }
    )  # fmt: skip


def test_kline_becomes_the_documented_candle_message() -> None:
    message = parse_kline(kline(closed=True), PAIRS)
    assert message == {
        "type": "candle",
        "symbol": "BTC",
        "tf": "1h",
        "candle": {
            "t": "2026-10-02T22:00:00Z", "o": "84531.68", "h": "84600.00",
            "l": "84500.10", "c": "84588.00", "v": "412.3", "closed": True,
        },
    }  # fmt: skip


def test_unknown_pairs_and_intervals_are_ignored() -> None:
    assert parse_kline(kline("DOGEUSDT"), PAIRS) is None
    assert parse_kline(kline(interval="15m"), PAIRS) is None
    assert parse_kline(json.dumps({"result": None, "id": 1}), PAIRS) is None


def test_fan_out_only_reaches_matching_clients() -> None:
    btc_1h, eth_4h = Client({"BTC"}, {"1h"}), Client({"ETH"}, {"4h"})
    hub.clients |= {btc_1h, eth_4h}
    try:
        hub.broadcast(parse_kline(kline(), PAIRS))
        assert btc_1h.queue.qsize() == 1 and eth_4h.queue.qsize() == 0
    finally:
        hub.clients -= {btc_1h, eth_4h}


def test_slow_client_keeps_only_the_newest_updates() -> None:
    client = Client({"BTC"}, {"1h"})
    for i in range(250):
        client.push({"n": i})
    assert client.queue.qsize() == 200
    assert client.queue.get_nowait() == {"n": 50}


@pytest.fixture
def known_pairs():
    hub.symbols_by_pair = dict(PAIRS)
    yield
    hub.symbols_by_pair = {}


def test_websocket_receives_subscribed_candles(known_pairs) -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/stream?symbols=btc&tf=1h") as ws:
        hub.broadcast(parse_kline(kline("ETHUSDT"), PAIRS))  # not subscribed: must not arrive
        hub.broadcast(parse_kline(kline("BTCUSDT"), PAIRS))
        message = ws.receive_json()
        assert message["symbol"] == "BTC" and message["candle"]["c"] == "84588.00"


@pytest.mark.parametrize("query", ["symbols=DOGE&tf=1h", "symbols=BTC&tf=5m", "tf=1h"])
def test_websocket_rejects_bad_requests(known_pairs, query: str) -> None:
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect), client.websocket_connect(f"/ws/stream?{query}") as ws:
        ws.receive_json()
