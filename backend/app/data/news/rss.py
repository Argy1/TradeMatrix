"""Read headlines from RSS 2.0 and Atom feeds (no API key needed).

A feed is text from the internet, so it is treated as untrusted: the download is capped, the
XML is parsed with `defusedxml` (which refuses DTDs, entities and external references, the
tools of XML "entity bomb" and file-reading attacks), and one broken item never breaks the rest.
"""

import html
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from defusedxml import DefusedXmlException
from defusedxml.ElementTree import ParseError, fromstring

from app.data.news.base import FeedError, Headline

if TYPE_CHECKING:  # only for type hints; parsing always goes through defusedxml
    from xml.etree.ElementTree import Element

MAX_FEED_BYTES = 2_000_000
MAX_TITLE_CHARS = 300
ATOM = "{http://www.w3.org/2005/Atom}"
# Link decorations that say where a click came from, not which article it is.
TRACKING_PARAMS = ("utm_", "fbclid", "gclid", "mc_cid", "mc_eid")


def clean_url(url: str) -> str:
    """The article's address without tracking parameters or #fragment.

    The URL is the unique key of a headline, so the same article must always give the same URL.
    """
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(TRACKING_PARAMS)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def _clean_title(raw: str | None) -> str:
    # Some feeds escape twice ("&amp;amp;"); unescape once more, then collapse whitespace.
    return " ".join(html.unescape(raw or "").split())[:MAX_TITLE_CHARS]


def _to_utc(value: datetime) -> datetime:
    return (value if value.tzinfo else value.replace(tzinfo=UTC)).astimezone(UTC)


def _rss_item(item: "Element") -> tuple[str | None, str | None, datetime]:
    return (
        item.findtext("title"),
        item.findtext("link"),
        parsedate_to_datetime(item.findtext("pubDate") or ""),  # "Wed, 07 Oct 2026 04:00:51 +0000"
    )


def _atom_entry(entry: "Element") -> tuple[str | None, str | None, datetime]:
    links = entry.findall(f"{ATOM}link")
    link = next((x for x in links if x.get("rel", "alternate") == "alternate"), None)
    when = entry.findtext(f"{ATOM}published") or entry.findtext(f"{ATOM}updated") or ""
    return (
        entry.findtext(f"{ATOM}title"),
        link.get("href") if link is not None else None,
        datetime.fromisoformat(when),  # "2026-10-07T04:00:51Z"
    )


def parse_feed(source: str, body: bytes) -> list[Headline]:
    """Headlines from an RSS 2.0 or Atom document. Items without a title, an http(s) link or
    a readable date are skipped."""
    try:
        # forbid_dtd: real feeds do not need a DTD, so a document that has one is refused.
        root = fromstring(body, forbid_dtd=True)
    except DefusedXmlException as exc:
        raise FeedError(f"{source}: refused unsafe XML ({type(exc).__name__})") from exc
    except ParseError as exc:
        raise FeedError(f"{source}: not valid XML ({exc})") from exc

    readers = [(root.iter("item"), _rss_item), (root.iter(f"{ATOM}entry"), _atom_entry)]
    headlines: list[Headline] = []
    for elements, read in readers:
        for element in elements:
            try:
                raw_title, raw_link, published = read(element)
            except (TypeError, ValueError):
                continue  # missing or unreadable date
            title, link = _clean_title(raw_title), (raw_link or "").strip()
            if not title or not link.startswith(("http://", "https://")):
                continue
            headlines.append(Headline(source, title, clean_url(link), _to_utc(published)))
    return headlines


class RssSource:
    def __init__(self, name: str, url: str, http: httpx.AsyncClient) -> None:
        self.name = name
        self._url = url
        self._http = http

    async def fetch(self) -> list[Headline]:
        try:
            async with self._http.stream("GET", self._url, follow_redirects=True) as response:
                response.raise_for_status()
                body = bytearray()
                # Read in pieces and stop early: a huge or endless response must not fill memory.
                async for chunk in response.aiter_bytes():
                    body += chunk
                    if len(body) > MAX_FEED_BYTES:
                        raise FeedError(f"{self.name}: feed is larger than {MAX_FEED_BYTES} bytes")
        except httpx.HTTPError as exc:
            raise FeedError(f"{self.name}: {type(exc).__name__}: {exc}") from exc
        return parse_feed(self.name, bytes(body))
