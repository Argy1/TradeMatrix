"""Rehearsal of the every-minute pipeline against the real database, keeping nothing.

    uv run python -m app.worker.rehearsal --minutes 30

One second after every minute it runs the same steps as `fast_close` (read the candles that
just closed for every coin, predict, fill in results) inside one transaction, measures how
long after the close the signals were ready, and then ROLLS THE TRANSACTION BACK. Nothing it
writes stays in the database.

Because every minute is rolled back, each run has to read all candles since the last ones
that are really stored, so it does a little more work than the live worker will. If the
rehearsal is fast enough, the live run is too.

It passes when at least 99% of the expected signals were made and, in 95% of the runs, the
one-minute signal was ready within 5 seconds of the close (docs/05, Gate 5b-2). The larger
sizes are done after it; their times are shown too.
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime, timedelta

import numpy as np

from app import db
from app.config import get_settings
from app.data import repo
from app.data.exchanges import get_exchange_client
from app.data.ingest import ingest_many
from app.ml.predict import (
    FrameCache,
    ModelCache,
    active_models,
    resolve_outcomes,
    run_predictions,
    warm_up,
)
from app.ml.storage import ModelStorage
from app.timeframes import FAST_TIMEFRAMES, floor_time
from app.worker.jobs import closed_fast_timeframes, fast_groups

START_SECOND = 1  # the live job starts one second after the minute
MIN_STORED = 0.99
MAX_DELAY = 5.0  # seconds from the close until the 1m signal is ready, for 95% of the runs


async def one_run(factory, client, cache: ModelCache, frames: FrameCache, blend_k: float) -> dict:
    started = datetime.now(UTC)
    close = floor_time(started, "1m")  # the candle close this run belongs to
    sizes = closed_fast_timeframes(started)
    expected = created = retried = 0
    errors: list[str] = []
    ready: dict[str, float] = {}  # seconds after the close at which each size was done
    async with factory() as session:
        transaction = await session.begin()
        try:
            assets = await repo.list_assets(session)
            # The same order as the live run: the one-minute signal first, then the rest.
            for group in fast_groups(sizes):
                expected += len(await active_models(session, group))
                ingested = await ingest_many(session, client, assets, group, now=started)
                predicted = await run_predictions(
                    session, cache, group, started, blend_k=blend_k, frames=frames
                )
                done = (datetime.now(UTC) - close).total_seconds()
                ready.update(dict.fromkeys(group, done))
                created += predicted["created"]
                retried += ingested["retried"]
                errors += ingested["errors"] + predicted["errors"]
            await resolve_outcomes(session, list(FAST_TIMEFRAMES), look_back=timedelta(hours=2))
        finally:
            await transaction.rollback()  # the whole point: nothing stays
    return {
        "close": close,
        "sizes": sizes,
        "expected": expected,
        "created": created,
        "errors": errors,
        "retried": retried,
        "ready": ready,
    }


async def rehearse(minutes: int) -> bool:
    settings = get_settings()
    factory = db.session_factory()
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    client = get_exchange_client(settings)
    storage = ModelStorage(
        settings.supabase_url, settings.supabase_service_role_key, settings.supabase_models_bucket
    )
    cache = ModelCache(storage)
    # Kept between the minutes, like in the live worker. The candles it holds are real
    # exchange candles, so it stays right although each minute's writes are rolled back.
    frames = FrameCache()
    runs: list[dict] = []
    try:
        # The live worker loads model files and candles at start-up; do the same here.
        async with factory() as session:
            warmed = await warm_up(session, cache, frames, list(FAST_TIMEFRAMES))
        print(f"warm-up: {warmed['models']} models loaded, errors: {warmed['errors']}", flush=True)
        for _ in range(minutes):
            now = datetime.now(UTC)
            next_start = floor_time(now, "1m") + timedelta(minutes=1, seconds=START_SECOND)
            await asyncio.sleep((next_start - now).total_seconds())
            run = await one_run(factory, client, cache, frames, settings.sentiment_blend_k)
            runs.append(run)
            others = max((s for tf, s in run["ready"].items() if tf != "1m"), default=None)
            print(
                f"{run['close']:%H:%M} sizes={','.join(run['sizes']):18} "
                f"signals={run['created']:3}/{run['expected']:3} "
                f"1m ready {run['ready']['1m']:.1f}s after the close"
                + (f", the larger sizes {others:.1f}s" if others is not None else "")
                + (f" (asked again for {run['retried']})" if run["retried"] else "")
                + (f"  errors={run['errors'][:2]}" if run["errors"] else ""),
                flush=True,
            )
    finally:
        await client.aclose()
        await storage.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()

    expected = sum(r["expected"] for r in runs)
    created = sum(r["created"] for r in runs)
    one_minute = np.array([r["ready"]["1m"] for r in runs])
    larger = np.array([s for r in runs for tf, s in r["ready"].items() if tf != "1m"])
    stored = created / expected if expected else 0.0
    p95 = float(np.percentile(one_minute, 95)) if len(one_minute) else float("nan")
    passed = stored >= MIN_STORED and p95 <= MAX_DELAY
    print(
        f"\n{len(runs)} runs: {created} of {expected} expected signals ({stored:.1%}). "
        f"1m ready after the close: median {np.median(one_minute):.1f}s, 95% within {p95:.1f}s, "
        f"slowest {one_minute.max():.1f}s."
        + (
            f" Larger sizes: median {np.median(larger):.1f}s, slowest {larger.max():.1f}s."
            if len(larger)
            else ""
        )
        + f" Errors: {sum(len(r['errors']) for r in runs)}."
    )
    print("PASSED" if passed else "NOT PASSED", f"(needs >= {MIN_STORED:.0%} and <= {MAX_DELAY}s)")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Rehearse the minute pipeline (rolled back).")
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()
    return 0 if asyncio.run(rehearse(args.minutes)) else 1


if __name__ == "__main__":
    sys.exit(main())
