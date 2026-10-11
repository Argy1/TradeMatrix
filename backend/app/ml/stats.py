"""Daily signal counts (`signal_stats_daily`) and the 90-day clean-up of the fast sizes.

    uv run python -m app.ml.stats --since 2026-10-01     # (re)build the counts from that day on

Why: the fast sizes make about 37,600 signals a day. Reading them one by one for the
track-record page would get slower every day, and keeping them forever would fill the
database. So the worker adds them up per coin, size and day (`summarize_signals`), the
track record reads those counts, and raw fast signals older than 90 days are deleted
(`prune_fast_history`) once their day is counted. The counts themselves are never deleted.
"""

import argparse
import asyncio
import sys
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.ml.performance import Totals
from app.timeframes import FAST_TIMEFRAMES, TIMEFRAMES, interval_case_sql

# A result exists when the candle closed up or down ('flat', on the fast sizes, has none).
_HAS_RESULT = "o.actual_direction in ('up', 'down')"
# The candle before the base candle, for the naive rule ("the next candle repeats the last").
_PREVIOUS = f"p.base_open_time - {interval_case_sql('p.timeframe')}"

# One coin and size at a time (the lateral part), so each step is a short walk through the
# index on (asset_id, timeframe, target_open_time), never a scan of the whole table.
_SUMMARIZE = text(
    f"""
    insert into signal_stats_daily (
      asset_id, timeframe, day, n_signals, n_resolved, n_flat, n_went_up, n_calls, n_correct,
      n_up_calls, n_up_correct, n_down_calls, n_down_correct, n_naive, n_naive_correct,
      brier_sum, updated_at)
    select a.id, tf.timeframe, s.*, now()
    from assets a
    cross join unnest(cast(:timeframes as text[])) as tf(timeframe)
    cross join lateral (
      select (p.target_open_time at time zone 'UTC')::date as day,
             count(*) as n_signals,
             count(*) filter (where {_HAS_RESULT}) as n_resolved,
             count(*) filter (where o.actual_direction = 'flat') as n_flat,
             count(*) filter (where o.actual_direction = 'up') as n_went_up,
             count(*) filter (where o.correct is not null) as n_calls,
             count(*) filter (where o.correct) as n_correct,
             count(*) filter (where o.correct is not null and p.label = 'up') as n_up_calls,
             count(*) filter (where o.correct and p.label = 'up') as n_up_correct,
             count(*) filter (where o.correct is not null and p.label = 'down') as n_down_calls,
             count(*) filter (where o.correct and p.label = 'down') as n_down_correct,
             count(*) filter (where {_HAS_RESULT} and prev.close is not null) as n_naive,
             count(*) filter (
               where {_HAS_RESULT} and prev.close is not null
                 and (p.base_close > prev.close) = (o.actual_direction = 'up')
             ) as n_naive_correct,
             coalesce(
               sum(power(p.p_up - (o.actual_direction = 'up')::int, 2))
                 filter (where {_HAS_RESULT}),
               0
             ) as brier_sum
      from predictions p
      left join prediction_outcomes o on o.prediction_id = p.id
      left join candles prev on prev.asset_id = p.asset_id
        and prev.timeframe = p.timeframe and prev.open_time = {_PREVIOUS}
      where p.asset_id = a.id and p.timeframe = tf.timeframe
        and p.target_open_time >= :since
      group by 1
    ) s
    on conflict (asset_id, timeframe, day) do update set
      n_signals = excluded.n_signals, n_resolved = excluded.n_resolved,
      n_flat = excluded.n_flat, n_went_up = excluded.n_went_up,
      n_calls = excluded.n_calls, n_correct = excluded.n_correct,
      n_up_calls = excluded.n_up_calls, n_up_correct = excluded.n_up_correct,
      n_down_calls = excluded.n_down_calls, n_down_correct = excluded.n_down_correct,
      n_naive = excluded.n_naive, n_naive_correct = excluded.n_naive_correct,
      brier_sum = excluded.brier_sum, updated_at = excluded.updated_at
    returning 1
    """
)


def day_start(moment: datetime) -> datetime:
    return moment.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


async def summarize_signals(
    session: AsyncSession,
    *,
    days_back: int = 2,
    now: datetime | None = None,
    since: datetime | None = None,
) -> dict:
    """Recount whole days, from `days_back` days ago (or `since`) until now.

    Idempotent: a day is always counted from its raw rows, so running it twice (or again an
    hour later, when more signals have their result) just writes the newer numbers.
    """
    since = since or day_start(now or datetime.now(UTC)) - timedelta(days=days_back)
    rows = await session.execute(_SUMMARIZE, {"timeframes": list(TIMEFRAMES), "since": since})
    return {"days": len(rows.all()), "since": since.date().isoformat()}


async def prune_fast_history(
    session: AsyncSession, *, keep_days: int, now: datetime | None = None
) -> dict:
    """Delete raw fast-size signals and candles older than `keep_days`.

    A signal is only deleted when its day has been counted at least two days after it was
    made: by then every signal of that day has its result, so the counts are final. (Its
    outcome row goes with it: prediction_outcomes deletes in cascade.) The slow sizes are
    never touched.
    """
    cutoff = day_start(now or datetime.now(UTC)) - timedelta(days=keep_days)
    fast = {"fast": list(FAST_TIMEFRAMES), "cutoff": cutoff}
    signals = await session.execute(
        text(
            """
            delete from predictions p
            using assets a, unnest(cast(:fast as text[])) as tf(timeframe)
            where p.asset_id = a.id and p.timeframe = tf.timeframe
              and p.target_open_time < :cutoff
              and exists (
                select 1 from signal_stats_daily s
                where s.asset_id = p.asset_id and s.timeframe = p.timeframe
                  and s.day = (p.target_open_time at time zone 'UTC')::date
                  and s.updated_at >= p.target_open_time + interval '2 days'
              )
            returning 1
            """
        ),
        fast,
    )
    candles = await session.execute(
        text(
            """
            delete from candles c
            using assets a, unnest(cast(:fast as text[])) as tf(timeframe)
            where c.asset_id = a.id and c.timeframe = tf.timeframe and c.open_time < :cutoff
            returning 1
            """
        ),
        fast,
    )
    return {
        "signals": len(signals.all()),
        "candles": len(candles.all()),
        "older_than": cutoff.date().isoformat(),
    }


_SUMS = """
    coalesce(sum(n_signals), 0), coalesce(sum(n_flat), 0),
    coalesce(sum(n_resolved), 0), coalesce(sum(n_went_up), 0), coalesce(sum(n_calls), 0),
    coalesce(sum(n_correct), 0), coalesce(sum(n_up_calls), 0), coalesce(sum(n_up_correct), 0),
    coalesce(sum(n_down_calls), 0), coalesce(sum(n_down_correct), 0), coalesce(sum(n_naive), 0),
    coalesce(sum(n_naive_correct), 0), coalesce(sum(brier_sum), 0)
"""


def _unpack(values: tuple) -> tuple[int, int, Totals]:
    """(signals, flat, Totals) from the columns of `_SUMS`."""
    return int(values[0]), int(values[1]), Totals(*map(int, values[2:12]), float(values[12]))


async def totals(
    session: AsyncSession, asset_id: int | None, timeframe: str | None, since: date
) -> tuple[int, int, Totals]:
    """Counts added up over the days from `since`, for one coin and size or for all of them."""
    row = (
        await session.execute(
            text(
                f"""
                select {_SUMS} from signal_stats_daily
                where (cast(:a as smallint) is null or asset_id = :a)
                  and (cast(:tf as text) is null or timeframe = :tf)
                  and day >= :since
                """
            ),
            {"a": asset_id, "tf": timeframe, "since": since},
        )
    ).one()
    return _unpack(tuple(row))


async def totals_by_pair(
    session: AsyncSession, timeframe: str | None, since: date
) -> dict[tuple[int, str], tuple[int, int, Totals]]:
    """The same per (asset_id, timeframe), in one query."""
    rows = await session.execute(
        text(
            f"""
            select asset_id, timeframe, {_SUMS} from signal_stats_daily
            where (cast(:tf as text) is null or timeframe = :tf) and day >= :since
            group by asset_id, timeframe
            """
        ),
        {"tf": timeframe, "since": since},
    )
    return {(row[0], row[1]): _unpack(tuple(row[2:])) for row in rows}


async def _rebuild(since: datetime) -> None:
    factory = db.session_factory()
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    try:
        async with factory() as session, session.begin():
            print(await summarize_signals(session, since=since))
    finally:
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="(Re)build signal_stats_daily from raw signals.")
    parser.add_argument("--since", required=True, help="first UTC day to count, e.g. 2026-10-01")
    args = parser.parse_args()
    asyncio.run(_rebuild(datetime.fromisoformat(args.since).replace(tzinfo=UTC)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
