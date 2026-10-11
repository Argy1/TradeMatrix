"""All SQL for market data lives here, as plain parameterized queries.

Why plain SQL: the queries are short, and reading them teaches more than an ORM layer would.
Values always travel as parameters (:name), never by string formatting.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.exchanges.base import Candle
from app.timeframes import TIMEFRAMES, last_closed_open_time, stale_grace

UPSERT_CHUNK = 2000


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
    insert into candles (asset_id, timeframe, open_time, open, high, low, close, volume,
                         trades, taker_buy_volume)
    values (:asset_id, :timeframe, :open_time, :open, :high, :low, :close, :volume,
            :trades, :taker_buy_volume)
    on conflict (asset_id, timeframe, open_time) do update
    set open = excluded.open, high = excluded.high, low = excluded.low,
        close = excluded.close, volume = excluded.volume,
        trades = excluded.trades, taker_buy_volume = excluded.taker_buy_volume
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
            "trades": c.trades,
            "taker_buy_volume": c.taker_buy_volume,
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


async def latest_open_times(
    session: AsyncSession, timeframes: Sequence[str]
) -> dict[tuple[int, str], datetime | None]:
    """Newest stored candle per (asset id, size) for every active coin, in one query."""
    rows = await session.execute(
        text(
            """
            select a.id, tf.timeframe,
                   (select max(open_time) from candles c
                    where c.asset_id = a.id and c.timeframe = tf.timeframe)
            from assets a
            cross join unnest(cast(:timeframes as text[])) as tf(timeframe)
            where a.active
            """
        ),
        {"timeframes": list(timeframes)},
    )
    return {(row[0], row[1]): row[2] for row in rows}


@dataclass(frozen=True)
class FeatureFrame:
    """The newest candles of one coin as numbers for the model, plus the exact last close."""

    frame: pd.DataFrame  # open, high, low, close, volume, trades, taker_buy_volume by open time
    last_close: Decimal


async def feature_frames(
    session: AsyncSession, asset_ids: Sequence[int], timeframe: str, limit: int
) -> dict[int, FeatureFrame]:
    """The newest `limit` candles of several coins in one query (oldest first per coin).

    The every-minute run predicts 16 coins at once; one query instead of two per coin keeps it
    inside a few seconds. Prices come back as floats because they only feed the model here;
    the one price that is stored again (the last close) also comes back exact.
    """
    rows = (
        await session.execute(
            text(
                """
                select c.asset_id, c.open_time,
                       c.open::float8, c.high::float8, c.low::float8, c.close::float8,
                       c.volume::float8, c.trades::float8, c.taker_buy_volume::float8, c.close
                from unnest(cast(:asset_ids as smallint[])) as a(id)
                cross join lateral (
                  select * from candles
                  where asset_id = a.id and timeframe = :timeframe
                  order by open_time desc limit :limit
                ) c
                order by c.asset_id, c.open_time
                """
            ),
            {"asset_ids": list(asset_ids), "timeframe": timeframe, "limit": limit},
        )
    ).all()
    columns = ["open", "high", "low", "close", "volume", "trades", "taker_buy_volume"]
    by_asset: dict[int, list] = {}
    for row in rows:
        by_asset.setdefault(row[0], []).append(row)
    return {
        asset_id: FeatureFrame(
            pd.DataFrame(
                [r[2:9] for r in group],
                columns=columns,
                index=pd.DatetimeIndex([r[1] for r in group]),
                dtype="float64",
            ),
            group[-1][9],
        )
        for asset_id, group in by_asset.items()
    }


async def earliest_open_time(
    session: AsyncSession, asset_id: int, timeframe: str
) -> datetime | None:
    return (
        await session.execute(
            text(
                "select min(open_time) from candles "
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
            from unnest(cast(:timeframes as text[])) as tf(timeframe)
            cross join assets a
            left join lateral (
              select max(open_time) as open_time from candles c
              where c.asset_id = a.id and c.timeframe = tf.timeframe
            ) as latest on true
            where a.active
            group by tf.timeframe
            having count(latest.open_time) = count(*)
            """
        ),
        {"timeframes": list(TIMEFRAMES)},
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


async def active_model_status(session: AsyncSession) -> list[tuple]:
    """(symbol, timeframe, model_version_id, trained_at, status) for every active model."""
    rows = await session.execute(
        text(
            """
            select a.symbol, m.timeframe, m.id, m.trained_at, m.status
            from model_versions m join assets a on a.id = m.asset_id
            where m.is_active order by m.timeframe, a.id
            """
        )
    )
    return [tuple(row) for row in rows]


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
    expected = last_closed_open_time(now - stale_grace(timeframe), timeframe)
    return latest is None or latest < expected
