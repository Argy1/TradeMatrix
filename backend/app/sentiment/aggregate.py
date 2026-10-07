"""One sentiment number per coin from its recent scored headlines (docs/03).

    weight        = 0.5 ** (age_hours / 6)                 a headline counts half after 6 hours
    sentiment_agg = sum(weight * score * confidence) / sum(weight)

Only the last 24 hours count. The result is about -1..+1, and 0 when there is no news.
"""

from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

WINDOW = timedelta(hours=24)
HALF_LIFE_HOURS = 6.0


def aggregate(rows: Iterable[tuple[datetime, float, float]], as_of: datetime) -> float:
    """`rows` = (published_at, score, confidence) of the headlines that mention one coin."""
    weighted = total = 0.0
    for published_at, score, confidence in rows:
        age = as_of - published_at
        if age < timedelta(0) or age > WINDOW:
            continue  # not known yet at `as_of`, or too old to matter
        weight = 0.5 ** (age.total_seconds() / 3600 / HALF_LIFE_HOURS)
        weighted += weight * score * confidence
        total += weight
    return weighted / total if total else 0.0


async def sentiment_by_asset(
    session: AsyncSession, symbols: Sequence[str], as_of: datetime
) -> dict[str, float]:
    """Aggregated sentiment for every coin, using only headlines published up to `as_of`.

    `as_of` is the moment the predicted candle opens. A headline published after that could
    not have been known when the signal was made, so it must never count (no leakage).
    """
    rows = (
        await session.execute(
            text(
                """
                select s.assets, n.published_at, s.score, s.confidence
                from sentiments s join news_items n on n.id = s.news_id
                where n.published_at > :since and n.published_at <= :as_of
                """
            ),
            {"since": as_of - WINDOW, "as_of": as_of},
        )
    ).all()
    return {
        symbol: aggregate(
            ((row.published_at, row.score, row.confidence) for row in rows if symbol in row.assets),
            as_of,
        )
        for symbol in symbols
    }
