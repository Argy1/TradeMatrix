"""Pick the exchange adapter named by the EXCHANGE variable."""

from app.config import Settings
from app.data.exchanges.base import Candle, ExchangeClient, ExchangeError
from app.data.exchanges.binance import BinanceClient

__all__ = ["Candle", "ExchangeClient", "ExchangeError", "get_exchange_client"]


def get_exchange_client(settings: Settings) -> ExchangeClient:
    if settings.exchange == "binance":
        return BinanceClient(settings.binance_rest_url)
    # bybit / okx / kraken are added only if Binance stops being reachable (docs/02).
    raise ValueError(f"Unsupported EXCHANGE '{settings.exchange}'")
