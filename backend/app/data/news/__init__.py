"""The news sources read by the `ingest_news` job."""

import httpx

from app.data.news.base import FeedError, Headline, NewsSource
from app.data.news.rss import RssSource

__all__ = ["FeedError", "Headline", "NewsSource", "get_news_sources", "news_http"]

# Public RSS feeds: free, no key, no account. They replace CryptoPanic, which is paid only
# (Argy, 2026-10-07). Chosen for editorial quality over volume: sites that mostly publish
# price predictions and sponsored posts would only add noise to the sentiment.
# Checked on 2026-10-07: each one answers, parses and has headlines from the last 24 hours.
RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
    "decrypt": "https://decrypt.co/feed",
    "theblock": "https://www.theblock.co/rss.xml",
    "bitcoinmagazine": "https://bitcoinmagazine.com/feed",
    "thedefiant": "https://thedefiant.io/feed",
}
# Says who is asking, which is polite towards the publishers and helps them contact us.
USER_AGENT = "TradeMatrixAI/1.0 (+https://tradematrix-rho.vercel.app)"


def news_http() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT})


def get_news_sources(http: httpx.AsyncClient) -> list[NewsSource]:
    return [RssSource(name, url, http) for name, url in RSS_FEEDS.items()]
