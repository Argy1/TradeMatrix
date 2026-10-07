"""News ingestion: reading feeds safely, cleaning links, tagging coins, dedupe keys."""

from datetime import UTC, datetime

import httpx
import pytest

from app.data.news import RSS_FEEDS, get_news_sources
from app.data.news.base import FeedError
from app.data.news.ingest import title_hash
from app.data.news.rss import MAX_FEED_BYTES, RssSource, clean_url, parse_feed
from app.data.news.tagging import NAMES, tag_assets

COINS = list(NAMES)

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Example feed</title>
    <item>
      <title><![CDATA[  Bitcoin   climbs as  traders &amp; funds return ]]></title>
      <link>https://news.example.test/a/bitcoin-climbs?utm_source=rss&amp;utm_medium=feed&amp;id=7#top</link>
      <pubDate>Wed, 07 Oct 2026 04:00:51 +0000</pubDate>
    </item>
    <item>
      <title>Evening note in Jakarta time</title>
      <link>https://news.example.test/a/evening-note</link>
      <pubDate>Wed, 07 Oct 2026 11:30:00 +0700</pubDate>
    </item>
    <item><title>No link here</title><pubDate>Wed, 07 Oct 2026 04:00:51 +0000</pubDate></item>
    <item><title>Bad date</title><link>https://news.example.test/a/bad</link><pubDate>soon</pubDate></item>
    <item><title>Not a web link</title><link>javascript:alert(1)</link>
      <pubDate>Wed, 07 Oct 2026 04:00:51 +0000</pubDate></item>
    <item><title></title><link>https://news.example.test/a/empty</link>
      <pubDate>Wed, 07 Oct 2026 04:00:51 +0000</pubDate></item>
  </channel>
</rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Example atom feed</title>
  <entry>
    <title>Ethereum upgrade goes live</title>
    <link rel="self" href="https://news.example.test/feed/1"/>
    <link rel="alternate" href="https://news.example.test/b/ethereum-upgrade"/>
    <published>2026-10-07T04:00:51Z</published>
  </entry>
</feed>"""

BOMB = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">]>
<rss version="2.0"><channel><item><title>&lol2;</title>
<link>https://news.example.test/x</link><pubDate>Wed, 07 Oct 2026 04:00:51 +0000</pubDate>
</item></channel></rss>"""


def test_rss_items_become_clean_headlines() -> None:
    headlines = parse_feed("example", RSS)
    assert [h.title for h in headlines] == [
        "Bitcoin climbs as traders & funds return",  # CDATA, double spaces and &amp; cleaned
        "Evening note in Jakarta time",
    ]  # the four broken items are skipped, they do not break the feed
    first, second = headlines
    assert first.source == "example"
    assert first.url == "https://news.example.test/a/bitcoin-climbs?id=7"  # no utm_, no #top
    assert first.published_at == datetime(2026, 10, 7, 4, 0, 51, tzinfo=UTC)
    assert second.published_at == datetime(2026, 10, 7, 4, 30, tzinfo=UTC)  # +07:00 -> UTC


def test_atom_entries_are_read_too() -> None:
    (headline,) = parse_feed("example", ATOM)
    assert headline.title == "Ethereum upgrade goes live"
    assert headline.url == "https://news.example.test/b/ethereum-upgrade"  # the article, not "self"
    assert headline.published_at == datetime(2026, 10, 7, 4, 0, 51, tzinfo=UTC)


def test_unsafe_or_broken_xml_is_refused() -> None:
    with pytest.raises(FeedError, match="unsafe"):
        parse_feed("example", BOMB)  # a DTD with entities: never expanded, never parsed
    with pytest.raises(FeedError, match="not valid XML"):
        parse_feed("example", b"<rss><channel><item>")
    assert parse_feed("example", b"<html><body>Service unavailable</body></html>") == []


def test_clean_url_keeps_what_identifies_the_article() -> None:
    assert clean_url(" https://a.test/x?utm_campaign=z&page=2&fbclid=abc#c ") == (
        "https://a.test/x?page=2"
    )
    assert clean_url("https://a.test/x") == "https://a.test/x"


def test_title_hash_ignores_case_and_punctuation() -> None:
    assert title_hash("Bitcoin hits $90,000!") == title_hash("bitcoin hits 90 000")
    assert title_hash("Bitcoin hits $90,000") != title_hash("Bitcoin hits $80,000")
    assert len(title_hash("anything")) == 32


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Bitcoin and Ethereum slide as dollar gains", ["BTC", "ETH"]),
        ("Bitcoin Cash jumps 10% after upgrade", ["BCH"]),  # not also BTC
        ("Ethereum Classic miners switch pools", []),  # a different coin we do not support
        ("Tether prints another billion", []),  # "ether" inside a word does not count
        ("Ether leads the market higher", ["ETH"]),
        ("Price holds near $84,000 as traders wait", []),  # "near" is just a word
        ("NEAR Protocol ships new sharding upgrade", ["NEAR"]),
        ("Traders rotate into NEAR and DOT", ["NEAR", "DOT"]),
        ("Chainlink (LINK) adds a new data feed", ["LINK"]),
        ("Read more at the link below", []),
        ("A stellar week for bitcoin miners", ["BTC"]),  # adjective, not the Stellar coin
        ("XLM rallies as Stellar Network upgrade lands", ["XLM"]),
        ("Ripple wins court ruling, $XRP up 8%", ["XRP"]),
        ("Rate cut sends ripple effects through markets", []),
        ("$SOL breaks out; Solana volume doubles", ["SOL"]),
        ("BNB Chain fees drop", ["BNB"]),
        ("Fed holds rates steady", []),
    ],
)
def test_tagging_only_counts_real_mentions(title: str, expected: list[str]) -> None:
    assert tag_assets(title, COINS) == expected


def test_tags_follow_the_given_coin_list() -> None:
    title = "Dogecoin and Bitcoin rally"
    assert tag_assets(title, ["DOGE", "BTC"]) == ["DOGE", "BTC"]  # the caller's order
    assert tag_assets(title, ["BTC"]) == ["BTC"]  # a coin that is not active is never tagged


def feed_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_source_downloads_and_parses() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=RSS)

    async with feed_client(handler) as http:
        headlines = await RssSource("example", "https://news.example.test/rss", http).fetch()
    assert len(headlines) == 2 and str(seen[0].url) == "https://news.example.test/rss"


async def test_source_errors_become_feed_errors() -> None:
    async with feed_client(lambda request: httpx.Response(503)) as http:
        with pytest.raises(FeedError, match="example"):
            await RssSource("example", "https://news.example.test/rss", http).fetch()

    def too_big(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<rss>" + b" " * (MAX_FEED_BYTES + 1))

    async with feed_client(too_big) as http:
        with pytest.raises(FeedError, match="larger than"):
            await RssSource("example", "https://news.example.test/rss", http).fetch()


async def test_default_sources_are_keyless_https_feeds() -> None:
    async with httpx.AsyncClient() as http:
        sources = get_news_sources(http)
    assert [s.name for s in sources] == list(RSS_FEEDS)
    assert len(RSS_FEEDS) >= 4  # several publishers, so one being down is not a blackout
    assert all(url.startswith("https://") for url in RSS_FEEDS.values())
