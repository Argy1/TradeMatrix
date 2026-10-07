"""Fetch headlines and store the new ones (the `ingest_news` job logic)."""

import hashlib
import re
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.news.base import Headline, NewsSource
from app.data.news.tagging import tag_assets

# Sentiment only looks back 24 hours (docs/03), so older feed items are not worth storing.
MAX_AGE = timedelta(days=3)
# Raw headlines are kept this long, so the database does not grow forever. The sentiment value
# that a signal actually used stays on its `predictions` row for good.
RETENTION = timedelta(days=90)


def title_hash(title: str) -> str:
    """The same headline gives the same hash, whatever its capitals or punctuation.

    Two sources often carry one story under the same title with different URLs. Counting it
    twice would double its weight in the sentiment, so the title is the second dedupe key.
    """
    normalized = " ".join(re.sub(r"[\W_]+", " ", title.casefold()).split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


# Idempotent in two ways: the URL is unique (on conflict do nothing), and a headline whose
# title was already stored in the last 3 days is skipped. Casts are spelled out because
# Postgres cannot guess parameter types inside "insert ... select".
_INSERT = text(
    """
    insert into news_items (source, title, url, title_hash, published_at, asset_symbols)
    select cast(:source as text), cast(:title as text), cast(:url as text),
           cast(:hash as text), cast(:published as timestamptz), cast(:symbols as text[])
    where not exists (
      select 1 from news_items n
      where n.title_hash = cast(:hash as text)
        and n.published_at > cast(:published as timestamptz) - interval '3 days'
    )
    on conflict (url) do nothing
    returning id
    """
)


async def store_headlines(
    session: AsyncSession, headlines: Sequence[Headline], symbols: Sequence[str], now: datetime
) -> int:
    """Insert the headlines we do not have yet; returns how many were new."""
    stored = 0
    for item in headlines:
        # A source whose clock runs ahead must not make its headline look like the newest.
        published = min(item.published_at, now)
        if now - published > MAX_AGE:
            continue
        inserted = await session.execute(
            _INSERT,
            {
                "source": item.source,
                "title": item.title,
                "url": item.url,
                "hash": title_hash(item.title),
                "published": published,
                "symbols": tag_assets(item.title, symbols),
            },
        )
        stored += inserted.first() is not None
    return stored


async def prune_old_news(session: AsyncSession, now: datetime) -> int:
    """Delete headlines past the retention period (their `sentiments` rows go with them)."""
    deleted = await session.execute(
        text("delete from news_items where published_at < :cutoff"), {"cutoff": now - RETENTION}
    )
    return deleted.rowcount


async def ingest_news(
    session: AsyncSession, sources: Sequence[NewsSource], *, now: datetime | None = None
) -> dict:
    now = now or datetime.now(UTC)
    symbols = [asset.symbol for asset in await repo.list_assets(session)]
    fetched = stored = 0
    errors: list[str] = []
    for source in sources:
        try:
            headlines = await source.fetch()
        except Exception as exc:  # one source being down must not block the others
            errors.append(f"{source.name}: {type(exc).__name__}: {exc}"[:200])
            continue
        fetched += len(headlines)
        stored += await store_headlines(session, headlines, symbols, now)
    pruned = await prune_old_news(session, now)
    return {"fetched": fetched, "stored": stored, "pruned": pruned, "errors": errors}
