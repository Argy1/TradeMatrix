"""Candle history in local Parquet files, for training and backtests of the fast sizes.

    uv run python -m app.data.history                          # every coin, every fast size
    uv run python -m app.data.history --symbols BTC --timeframes 1m

Why files and not the database: one year of 1m candles for 16 coins is about 8 million rows.
The database keeps only what the live system needs (charts and the newest features); training
reads these files instead. Each run continues after the newest stored candle, so it can be
stopped and repeated at any time.
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from app import db
from app.config import BACKEND_DIR, get_settings
from app.data import repo
from app.data.exchanges import ExchangeClient, get_exchange_client
from app.data.exchanges.base import Candle
from app.timeframes import ALL_TIMEFRAMES, FAST_TIMEFRAMES, floor_time

HISTORY_DIR = BACKEND_DIR / "data" / "history"  # git-ignored (backend/.gitignore)

# How far back each size goes. Shorter candles get a shorter history: they already have far
# more rows, and very old one-minute behaviour says little about today's market.
HISTORY_DAYS = {"1m": 365, "3m": 548, "5m": 730, "15m": 1095, "30m": 1095}

COLUMNS = ["open", "high", "low", "close", "volume", "trades", "taker_buy_volume"]
CHUNK = 20_000  # candles per request series; the file is saved after each one
PARALLEL = 4  # downloads at the same time (stays far below the exchange's rate limit)


def path_for(symbol: str, timeframe: str) -> Path:
    return HISTORY_DIR / f"{symbol}_{timeframe}.parquet"


def to_frame(candles: list[Candle]) -> pd.DataFrame:
    """Candles as float columns indexed by open time (UTC). Floats are fine here: the files
    feed the model, they are never shown as prices."""
    return pd.DataFrame(
        {
            "open": [float(c.open) for c in candles],
            "high": [float(c.high) for c in candles],
            "low": [float(c.low) for c in candles],
            "close": [float(c.close) for c in candles],
            "volume": [float(c.volume) for c in candles],
            "trades": [float(c.trades or 0) for c in candles],
            "taker_buy_volume": [float(c.taker_buy_volume or 0) for c in candles],
        },
        index=pd.DatetimeIndex([c.open_time for c in candles], name="open_time"),
        columns=COLUMNS,
        dtype="float64",
    )


def load(symbol: str, timeframe: str) -> pd.DataFrame:
    """The stored history of one coin and size, oldest first."""
    path = path_for(symbol, timeframe)
    if not path.exists():
        raise FileNotFoundError(
            f"No history file for {symbol} {timeframe}. Run: uv run python -m app.data.history"
        )
    return pd.read_parquet(path)


def save(frame: pd.DataFrame, symbol: str, timeframe: str) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = path_for(symbol, timeframe)
    # Write next to the file, then swap: a stopped run can never leave half a file behind.
    partial = path.with_suffix(".partial")
    frame.to_parquet(partial)
    partial.replace(path)


async def update(
    client: ExchangeClient,
    symbol: str,
    exchange_symbol: str,
    timeframe: str,
    *,
    now: datetime | None = None,
    chunk: int = CHUNK,
) -> int:
    """Download every closed candle that is not in the file yet. Returns how many were added."""
    now = now or datetime.now(UTC)
    step = ALL_TIMEFRAMES[timeframe]
    path = path_for(symbol, timeframe)
    stored = pd.read_parquet(path) if path.exists() else None
    if stored is not None and len(stored):
        cursor = stored.index[-1].to_pydatetime() + step
    else:
        cursor = floor_time(now - timedelta(days=HISTORY_DAYS[timeframe]), timeframe)
    added = 0
    while cursor <= now:
        candles = await client.get_klines(exchange_symbol, timeframe, start=cursor, limit=chunk)
        if not candles:
            break
        fresh = to_frame(candles)
        stored = fresh if stored is None else pd.concat([stored, fresh])
        # Keep one row per open time, in order, whatever the exchange sent.
        stored = stored[~stored.index.duplicated(keep="last")].sort_index()
        save(stored, symbol, timeframe)
        added += len(fresh)
        cursor = candles[-1].open_time + step
        if len(candles) < chunk:
            break  # a short series means we reached the newest closed candle
    return added


async def run(symbols: list[str], timeframes: list[str]) -> None:
    factory = db.session_factory()
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured (it holds the list of coins)")
    async with factory() as session:
        assets = [a for a in await repo.list_assets(session) if not symbols or a.symbol in symbols]
    client = get_exchange_client(get_settings())
    gate = asyncio.Semaphore(PARALLEL)

    async def one(asset: repo.Asset, timeframe: str) -> None:
        async with gate:
            added = await update(client, asset.symbol, asset.exchange_symbol, timeframe)
            total = len(load(asset.symbol, timeframe))
            print(
                f"{asset.symbol:5} {timeframe:3} +{added:>7} candles, {total:>7} in file",
                flush=True,
            )

    try:
        # Small sizes last: they are the long downloads, and the others are usable meanwhile.
        order = sorted(timeframes, key=lambda tf: ALL_TIMEFRAMES[tf], reverse=True)
        await asyncio.gather(*(one(asset, tf) for tf in order for asset in assets))
    finally:
        await client.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download candle history into Parquet files.")
    parser.add_argument("--symbols", default="", help="default: every active coin")
    parser.add_argument("--timeframes", default=",".join(FAST_TIMEFRAMES))
    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    timeframes = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    unknown = [t for t in timeframes if t not in HISTORY_DAYS]
    if unknown:
        parser.error(f"no history length set for: {', '.join(unknown)}")
    asyncio.run(run(symbols, timeframes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
