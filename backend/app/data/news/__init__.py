"""The news sources read by the `ingest_news` job."""

import httpx

from app.data.news.base import FeedError, Headline, NewsSource
from app.data.news.rss import RssSource

__all__ = ["FeedError", "Headline", "NewsSource", "get_news_sources", "news_http"]

# Public RSS feeds, no key needed. CryptoPanic (docs/02) is added here once Argy has confirmed
# a plan and put CRYPTOPANIC_API_KEY on Railway; the job itself will not change.
RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
}
# Says who is asking, which is polite towards the publishers and helps them contact us.
USER_AGENT = "TradeMatrixAI/1.0 (+https://tradematrix-rho.vercel.app)"


def news_http() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT})


def get_news_sources(http: httpx.AsyncClient) -> list[NewsSource]:
    return [RssSource(name, url, http) for name, url in RSS_FEEDS.items()]
