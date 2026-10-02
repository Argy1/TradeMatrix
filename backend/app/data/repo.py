"""All SQL for market data lives here, as plain parameterized queries.

Why plain SQL: the queries are short, and reading them teaches more than an ORM layer would.
Values always travel as parameters (:name), never by string formatting.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.exchanges.base import Candle
from app.timeframes import TIMEFRAMES, last_closed_open_time

UPSERT_CHUNK = 2000
STALE_GRACE = timedelta(minutes=3)


@dataclass(frozen=True, slots=True)
class Asset:
    id: int
    symbol: str
    name: str
    exchange_symbol: str


@dataclass(frozen=True, slots=True)
class Heartbeat:
    job_name: str
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None


async def list_assets(session: AsyncSession) -> list[Asset]:
    rows = await session.execute(
        text("select id, symbol, name, exchange_symbol from assets where active order by id")
    )
    return [Asset(*row) for row in rows]


async def get_asset(session: AsyncSession, symbol: str) -> Asset | None:
    row = (
        await session.execute(
            text(
                "select id, symbol, name, exchange_symbol from assets "
                "where symbol = :symbol and active"
            ),
            {"symbol": symbol},
        )
    ).first()
    return Asset(*row) if row else None


_UPSERT = text(
    """
    insert into candles (asset_id, timeframe, open_time, open, high, low, close, volume)
    values (:asset_id, :timeframe, :open_time, :open, :high, :low, :close, :volume)
    on conflict (asset_id, timeframe, open_time) do update
    set open = excluded.open, high = excluded.high, low = excluded.low,
        close = excluded.close, volume = excluded.volume
    """
)


async def upsert_candles(
    session: AsyncSession, asset_id: int, timeframe: str, candles: Sequence[Candle]
) -> int:
    """Insert candles, or overwrite the row if that candle is already stored.

    The primary key (asset_id, timeframe, open_time) makes this idempotent: running it
    twice with the same candles leaves exactly one row per candle.
    """
    rows = [
        {
            "asset_id": asset_id,
            "timeframe": timeframe,
            "open_time": c.open_time,
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        }
        for c in candles
    ]
    for start in range(0, len(rows), UPSERT_CHUNK):
        await session.execute(_UPSERT, rows[start : start + UPSERT_CHUNK])
    return len(rows)


async def latest_open_time(session: AsyncSession, asset_id: int, timeframe: str) -> datetime | None:
    return (
        await session.execute(
            text(
                "select max(open_time) from candles "
                "where asset_id = :asset_id and timeframe = :timeframe"
            ),
            {"asset_id": asset_id, "timeframe": timeframe},
        )
    ).scalar_one()


async def fetch_candles(
    session: AsyncSession,
    asset_id: int,
    timeframe: str,
    limit: int,
    before: datetime | None = None,
) -> list[Candle]:
    """The newest `limit` candles that opened before `before`, returned oldest first."""
    rows = await session.execute(
        text(
            """
            select open_time, open, high, low, close, volume from candles
            where asset_id = :asset_id and timeframe = :timeframe
              and (cast(:before as timestamptz) is null or open_time < :before)
            order by open_time desc
            limit :limit
            """
        ),
        {"asset_id": asset_id, "timeframe": timeframe, "before": before, "limit": limit},
    )
    return [Candle(*row) for row in rows][::-1]


async def count_candles(session: AsyncSession, asset_id: int, timeframe: str) -> int:
    return (
        await session.execute(
            text(
                "select count(*) from candles where asset_id = :asset_id and timeframe = :timeframe"
            ),
            {"asset_id": asset_id, "timeframe": timeframe},
        )
    ).scalar_one()


async def find_gaps(
    session: AsyncSession, asset_id: int, timeframe: str
) -> list[tuple[datetime, datetime]]:
    """Pairs (previous open time, next open time) where candles are missing in between."""
    rows = await session.execute(
        text(
            """
            select previous, open_time from (
              select open_time, lag(open_time) over (order by open_time) as previous
              from candles where asset_id = :asset_id and timeframe = :timeframe
            ) as ordered
            where open_time - previous > :step
            order by open_time
            """
        ),
        {"asset_id": asset_id, "timeframe": timeframe, "step": TIMEFRAMES[timeframe]},
    )
    return [(row[0], row[1]) for row in rows]


async def oldest_latest_candle(session: AsyncSession) -> dict[str, datetime | None]:
    """Per timeframe, the latest stored candle of the asset that is furthest behind."""
    rows = await session.execute(
        text(
            """
            select tf.timeframe, min(latest.open_time)
            from (values ('1h'), ('4h'), ('1d')) as tf(timeframe)
            cross join assets a
            left join lateral (
              select max(open_time) as open_time from candles c
              where c.asset_id = a.id and c.timeframe = tf.timeframe
            ) as latest on true
            where a.active
            group by tf.timeframe
            having count(latest.open_time) = count(*)
            """
        )
    )
    found = {row[0]: row[1] for row in rows}
    return {timeframe: found.get(timeframe) for timeframe in TIMEFRAMES}


async def record_heartbeat(session: AsyncSession, job_name: str, error: str | None = None) -> None:
    """Remember when a job last ran and whether it worked (shown by /v1/status)."""
    await session.execute(
        text(
            """
            insert into worker_heartbeat (job_name, last_run_at, last_success_at, last_error)
            values (:job_name, now(),
                    -- the cast tells Postgres the type even when error is NULL
                    case when cast(:error as text) is null then now() end, cast(:error as text))
            on conflict (job_name) do update
            set last_run_at = now(),
                last_success_at = coalesce(
                  excluded.last_success_at, worker_heartbeat.last_success_at),
                last_error = excluded.last_error
            """
        ),
        {"job_name": job_name, "error": error},
    )


async def list_heartbeats(session: AsyncSession) -> list[Heartbeat]:
    rows = await session.execute(
        text(
            "select job_name, last_run_at, last_success_at, last_error "
            "from worker_heartbeat order by job_name"
        )
    )
    return [Heartbeat(*row) for row in rows]


def is_stale(latest: datetime | None, timeframe: str, now: datetime) -> bool:
    """True if the newest stored candle is older than the one we should already have.

    The worker stores a candle a few seconds after it closes, so we allow a short grace
    period before calling the data stale.
    """
    expected = last_closed_open_time(now - STALE_GRACE, timeframe)
    return latest is None or latest < expected
