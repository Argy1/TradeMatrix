"""Score the headlines that have no sentiment yet (the `score_sentiment` job logic)."""

from datetime import UTC, datetime, timedelta
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.sentiment.aggregate import WINDOW
from app.sentiment.schemas import HeadlineSentiment, ToScore

MAX_TRIES = 3


class Scorer(Protocol):
    model: str
    prompt_version: str

    async def score(
        self, headlines: list[ToScore], symbols: list[str]
    ) -> list[HeadlineSentiment]: ...


async def scored_today(session: AsyncSession, now: datetime) -> int:
    """Headlines scored since 00:00 UTC. Counted from the table, so a worker restart cannot
    reset the daily budget."""
    day_start = now.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        text(
            "select count(*) from sentiments "
            "where created_at >= :day_start and created_at < :day_end"
        ),
        {"day_start": day_start, "day_end": day_start + timedelta(days=1)},
    )
    return result.scalar_one()


async def unscored(
    session: AsyncSession, now: datetime, limit: int, skip: list[int] | None = None
) -> list[ToScore]:
    """Newest first. Headlines older than the sentiment window can no longer change any
    signal, so they are never sent (and never cost anything)."""
    rows = await session.execute(
        text(
            """
            select n.id, n.source, n.title, n.published_at
            from news_items n
            where n.published_at > :since
              and n.id <> all(cast(:skip as bigint[]))
              and not exists (select 1 from sentiments s where s.news_id = n.id)
            order by n.published_at desc, n.id desc
            limit :limit
            """
        ),
        {"since": now - WINDOW, "limit": limit, "skip": skip or []},
    )
    return [ToScore(*row) for row in rows]


async def store_scores(
    session: AsyncSession, results: list[HeadlineSentiment], scorer: Scorer
) -> int:
    stored = 0
    for item in results:
        # The primary key is news_id: a headline is scored once, and a repeat is ignored.
        inserted = await session.execute(
            text(
                """
                insert into sentiments (news_id, assets, score, confidence, event_type, reason,
                  model, prompt_version)
                values (:news_id, cast(:assets as text[]), :score, :confidence, :event_type,
                  :reason, :model, :prompt_version)
                on conflict (news_id) do nothing
                returning news_id
                """
            ),
            {
                "news_id": item.id,
                "assets": item.assets,
                "score": item.score,
                "confidence": item.confidence,
                "event_type": item.event_type,
                "reason": item.reason,
                "model": scorer.model,
                "prompt_version": scorer.prompt_version,
            },
        )
        stored += inserted.first() is not None
    return stored


async def score_sentiment(
    session: AsyncSession,
    scorer: Scorer,
    *,
    max_per_run: int,
    batch_size: int,
    max_per_day: int,
    now: datetime | None = None,
    tries: dict[int, int] | None = None,
) -> dict:
    """`tries` (kept by the worker between runs) counts how often a headline was sent without
    getting a valid score. After MAX_TRIES it is left alone, so one headline the model cannot
    handle does not cost a request every 15 minutes."""
    now = now or datetime.now(UTC)
    tries = tries if tries is not None else {}
    # Budget guard (docs/03, docs/06): never more than `max_per_day` headlines per UTC day.
    room = min(max_per_run, max_per_day - await scored_today(session, now))
    if room <= 0:
        return {"scored": 0, "requests": 0, "budget_reached": True, "errors": []}
    given_up = [news_id for news_id, count in tries.items() if count >= MAX_TRIES]
    todo = await unscored(session, now, room, given_up)
    symbols = [asset.symbol for asset in await repo.list_assets(session)]
    scored = requests = 0
    errors: list[str] = []
    for start in range(0, len(todo), batch_size):
        batch = todo[start : start + batch_size]
        requests += 1
        try:
            results = await scorer.score(batch, symbols)
        except Exception as exc:
            # Usually the whole service or the key: stop now, the next run tries again.
            errors.append(f"{type(exc).__name__}: {exc}"[:200])
            break
        answered = {item.id for item in results}
        for headline in batch:
            if headline.id not in answered:
                tries[headline.id] = tries.get(headline.id, 0) + 1
        scored += await store_scores(session, results, scorer)
    return {
        "scored": scored,
        "requests": requests,
        "waiting": len(todo) - scored,
        "budget_reached": False,
        "errors": errors,
    }
