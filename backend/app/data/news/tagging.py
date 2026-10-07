"""Tag a headline with the supported coins it mentions (plain keywords, no AI).

This is a cheap first pass, stored on `news_items.asset_symbols` and used to filter the news
list. It is deliberately careful: several tickers are also normal English words ("near",
"link", "dot", "uni"), so a ticker only counts when written in capitals, and a coin name only
counts as a whole word. Gemini later gives its own, better list of affected coins.
"""

import re
from collections.abc import Iterable

# Names matched as whole words, any letter case. The ticker itself (BTC, $BTC) is always added.
NAMES: dict[str, tuple[str, ...]] = {
    "BTC": ("bitcoin",),
    "ETH": ("ethereum", "ether"),
    "SOL": ("solana",),
    "BNB": ("bnb", "binance coin"),
    "XRP": ("xrp", "ripple"),
    "DOGE": ("dogecoin",),
    "ADA": ("cardano",),
    "LINK": ("chainlink",),
    "AVAX": ("avalanche",),
    "UNI": ("uniswap",),
    "NEAR": ("near protocol",),
    "LTC": ("litecoin",),
    "TRX": ("tron",),
    "DOT": ("polkadot",),
    "BCH": ("bitcoin cash",),
    # Not plain "stellar": headlines use it as an adjective ("a stellar rally").
    "XLM": ("stellar lumens", "stellar network", "stellar foundation"),
}
# Phrases that contain a coin name but are about something else.
IGNORE = ("ethereum classic", "bitcoin sv", "bitcoin gold", "ripple effect", "ripple effects")


def _phrase(text: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(text)}(?![A-Za-z0-9])", re.IGNORECASE)


# Longest first, so "bitcoin cash" is found (and removed) before "bitcoin" gets a chance.
_PHRASES: list[tuple[re.Pattern[str], str | None]] = sorted(
    [(_phrase(name), symbol) for symbol, names in NAMES.items() for name in names]
    + [(_phrase(phrase), None) for phrase in IGNORE],
    key=lambda pair: -len(pair[0].pattern),
)


def tag_assets(title: str, symbols: Iterable[str]) -> list[str]:
    """The coins from `symbols` that the headline mentions, in the order of `symbols`."""
    wanted = list(symbols)
    found: set[str] = set()
    rest = title
    for pattern, symbol in _PHRASES:
        rest, hits = pattern.subn(" ", rest)
        if hits and symbol:
            found.add(symbol)
    for symbol in wanted:
        # Case-sensitive on purpose: "NEAR" is the coin, "near" is just a word.
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(symbol)}(?![A-Za-z0-9])", rest):
            found.add(symbol)
    return [symbol for symbol in wanted if symbol in found]
