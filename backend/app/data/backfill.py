"""Load candle history into the database.

    uv run python -m app.data.backfill                       # all coins, 1h + 4h + 1d
    uv run python -m app.data.backfill --symbols BTC,ETH --timeframes 1h
    uv run python -m app.data.backfill --since 2020-09-01    # also load older history

Safe to run again at any time: it only fetches what is missing.
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime

from app import db
from app.config import get_settings
from app.data import repo
from app.data.exchanges import ExchangeError, get_exchange_client
from app.data.ingest import extend_history, ingest_candles
from app.timeframes import TIMEFRAMES


async def run(
    symbols: list[str] | None, timeframes: list[str], since: datetime | None = None
) -> int:
    factory = db.session_factory()
    if factory is None:
        print("DATABASE_URL is not configured. Fill it in the root .env first.")
        return 1

    client = get_exchange_client(get_settings())
    failures = 0
    try:
        async with factory() as session:
            assets = [
                a for a in await repo.list_assets(session) if not symbols or a.symbol in symbols
            ]
            for asset in assets:
                for timeframe in timeframes:
                    try:
                        result = await ingest_candles(session, client, asset, timeframe)
                        if since is not None:
                            older = await extend_history(session, client, asset, timeframe, since)
                            result.fetched += older.fetched
                            result.stored += older.stored
                    except ExchangeError as exc:
                        failures += 1
                        await session.rollback()
                        print(f"{asset.symbol:4} {timeframe:3} FAILED: {exc}")
                        continue
                    total = await repo.count_candles(session, asset.id, timeframe)
                    gaps = await repo.find_gaps(session, asset.id, timeframe)
                    print(
                        f"{asset.symbol:4} {timeframe:3} fetched={result.fetched:6} "
                        f"stored={result.stored:6} total={total:6} "
                        f"gaps_in_db={len(gaps)} ({result.quality.summary()})"
                    )
                    for previous, following in gaps[:5]:
                        print(
                            f"       gap: {previous:%Y-%m-%d %H:%M} to {following:%Y-%m-%d %H:%M}"
                        )
            error = f"{failures} asset/timeframe runs failed" if failures else None
            await repo.record_heartbeat(session, "ingest_candles", error)
            await session.commit()
    finally:
        await client.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill candles from the exchange.")
    parser.add_argument("--symbols", help="comma-separated, e.g. BTC,ETH (default: all active)")
    parser.add_argument("--timeframes", default=",".join(TIMEFRAMES), help="default: 1h,4h,1d")
    parser.add_argument("--since", help="also load history back to this UTC date, e.g. 2020-09-01")
    args = parser.parse_args()
    timeframes = [t for t in args.timeframes.split(",") if t]
    unknown = [t for t in timeframes if t not in TIMEFRAMES]
    if unknown:
        parser.error(f"unknown timeframes: {unknown}")
    symbols = [s.upper() for s in args.symbols.split(",")] if args.symbols else None
    since = datetime.fromisoformat(args.since).replace(tzinfo=UTC) if args.since else None
    return asyncio.run(run(symbols, timeframes, since))


if __name__ == "__main__":
    sys.exit(main())
