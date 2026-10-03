"""Live updates over WebSocket: /ws/stream (docs/04).

    connect:  /ws/stream?symbols=BTC,ETH&tf=1h
    server -> {"type": "candle" | "prediction" | "ping", ...}
    client -> {"type": "subscribe" | "unsubscribe", "symbols": [...], "tf": "4h"}
              or {"type": "pong"}

One upstream connection to Binance's market-data stream feeds every browser (fan-out), so
a thousand viewers still cost one exchange connection. New predictions are found by polling the
database every 5 seconds (simple, works through the Supabase pooler; docs/02).
"""

import asyncio
import contextlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

import websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from app import db
from app.api.errors import ApiError
from app.timeframes import TIMEFRAMES

logger = logging.getLogger("stream")
router = APIRouter()

MAX_SYMBOLS = 10
PING_EVERY = 20  # seconds
IDLE_LIMIT = 60  # close the connection after this long without a pong
POLL_EVERY = 5


@dataclass(eq=False)
class Client:
    symbols: set[str]
    timeframes: set[str]
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=200))
    last_pong: float = field(default_factory=time.monotonic)

    def wants(self, symbol: str, timeframe: str) -> bool:
        return symbol in self.symbols and timeframe in self.timeframes

    def push(self, message: dict) -> None:
        # A slow browser must never slow down everyone else: drop its oldest updates.
        if self.queue.full():
            with contextlib.suppress(asyncio.QueueEmpty):
                self.queue.get_nowait()
        self.queue.put_nowait(message)


def parse_kline(raw: str, symbols_by_pair: dict[str, str]) -> dict | None:
    """Binance combined-stream kline message -> our candle message (prices stay strings)."""
    data = json.loads(raw).get("data", {})
    k = data.get("k")
    if not k or k.get("s") not in symbols_by_pair or k.get("i") not in TIMEFRAMES:
        return None
    return {
        "type": "candle",
        "symbol": symbols_by_pair[k["s"]],
        "tf": k["i"],
        "candle": {
            "t": datetime.fromtimestamp(k["t"] / 1000, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "o": k["o"],
            "h": k["h"],
            "l": k["l"],
            "c": k["c"],
            "v": k["v"],
            "closed": bool(k["x"]),
        },
    }


class StreamHub:
    def __init__(self) -> None:
        self.clients: set[Client] = set()
        self.symbols_by_pair: dict[str, str] = {}
        self._tasks: list[asyncio.Task] = []

    def broadcast(self, message: dict) -> None:
        for client in list(self.clients):
            if client.wants(message["symbol"], message["tf"]):
                client.push(message)

    async def start(self, ws_url: str) -> None:
        factory = db.session_factory()
        if factory is None:
            return
        async with factory() as session:
            rows = await session.execute(
                text("select exchange_symbol, symbol from assets where active")
            )
            self.symbols_by_pair = {pair: symbol for pair, symbol in rows}
        self._tasks = [
            asyncio.create_task(self._upstream(ws_url)),
            asyncio.create_task(self._poll_predictions()),
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def _upstream(self, ws_url: str) -> None:
        streams = "/".join(
            f"{pair.lower()}@kline_{tf}" for pair in self.symbols_by_pair for tf in TIMEFRAMES
        )
        delay = 1.0
        while True:
            try:
                async with websockets.connect(f"{ws_url}/stream?streams={streams}") as upstream:
                    delay = 1.0
                    async for raw in upstream:
                        message = parse_kline(raw, self.symbols_by_pair)
                        if message:
                            self.broadcast(message)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # network trouble: wait and reconnect, never crash the API
                logger.warning("upstream stream error, reconnecting in %.0fs: %s", delay, exc)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30.0)

    async def _poll_predictions(self) -> None:
        from app.api.signals import latest_prediction  # avoid an import cycle at startup

        factory = db.session_factory()
        last_id: int | None = None
        while True:
            try:
                async with factory() as session:
                    if last_id is None:
                        last_id = (
                            await session.execute(
                                text("select coalesce(max(id), 0) from predictions")
                            )
                        ).scalar_one()
                    rows = (
                        await session.execute(
                            text(
                                "select p.id, a.symbol, p.timeframe from predictions p "
                                "join assets a on a.id = p.asset_id "
                                "where p.id > :last order by p.id"
                            ),
                            {"last": last_id},
                        )
                    ).all()
                    for pid, symbol, timeframe in rows:
                        last_id = pid
                        if any(c.wants(symbol, timeframe) for c in self.clients):
                            prediction = await latest_prediction(session, symbol, timeframe)
                            self.broadcast(
                                {
                                    "type": "prediction",
                                    "symbol": symbol,
                                    "tf": timeframe,
                                    "prediction": prediction.model_dump(mode="json"),
                                }
                            )
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # keep polling even if one round fails
                logger.warning("prediction poll failed: %s", exc)
            await asyncio.sleep(POLL_EVERY)


hub = StreamHub()


def _parse_symbols(raw: str | list) -> set[str]:
    items = raw.split(",") if isinstance(raw, str) else raw
    return {str(s).strip().upper() for s in items if str(s).strip()}


@router.websocket("/ws/stream")
async def stream(websocket: WebSocket, symbols: str = "", tf: str = "1h") -> None:
    wanted = _parse_symbols(symbols)
    known = set(hub.symbols_by_pair.values())
    if (
        tf not in TIMEFRAMES
        or not wanted
        or len(wanted) > MAX_SYMBOLS
        or (known and wanted - known)
    ):
        await websocket.close(code=1008, reason="invalid symbols or tf")
        return
    await websocket.accept()
    client = Client(wanted, {tf})
    hub.clients.add(client)

    async def send() -> None:
        while True:
            await websocket.send_json(await client.queue.get())

    async def ping() -> None:
        while True:
            await asyncio.sleep(PING_EVERY)
            if time.monotonic() - client.last_pong > IDLE_LIMIT:
                await websocket.close(code=1000, reason="idle")
                return
            client.push({"type": "ping"})

    tasks = [asyncio.create_task(send()), asyncio.create_task(ping())]
    try:
        while True:
            message = await websocket.receive_json()
            kind = message.get("type")
            client.last_pong = time.monotonic()
            if kind in ("subscribe", "unsubscribe"):
                change = _parse_symbols(message.get("symbols", []))
                if message.get("tf") in TIMEFRAMES:
                    client.timeframes = {message["tf"]}
                if kind == "subscribe":
                    client.symbols = (
                        (client.symbols | change)
                        if len(client.symbols | change) <= MAX_SYMBOLS
                        else client.symbols
                    )
                else:
                    client.symbols -= change
    except (WebSocketDisconnect, ApiError, ValueError, RuntimeError):
        pass
    finally:
        hub.clients.discard(client)
        for task in tasks:
            task.cancel()
