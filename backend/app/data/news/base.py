"""News source interface.

The worker only talks to `NewsSource`, so a new source (another RSS feed, CryptoPanic) is one
new object in `get_news_sources`, with no change to the ingest job.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class FeedError(Exception):
    """A source could not be read or sent something we refuse to parse."""


@dataclass(frozen=True, slots=True)
class Headline:
    source: str
    title: str
    url: str
    published_at: datetime  # timezone-aware, UTC


class NewsSource(Protocol):
    name: str

    async def fetch(self) -> list[Headline]:
        """The newest headlines of this source. Raises FeedError when it cannot be read."""
        ...
