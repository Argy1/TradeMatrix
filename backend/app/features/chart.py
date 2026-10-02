"""Indicator series for the chart endpoint (the clients only draw what this returns)."""

from collections.abc import Sequence

import pandas as pd

from app.data.exchanges.base import Candle
from app.features import indicators as ind

# Extra candles loaded before the requested range so the first returned candle already
# has settled indicator values (EMA 50 and MACD need history to converge).
WARMUP = 250


def indicator_rows(candles: Sequence[Candle]) -> list[dict[str, float | None]]:
    """One dict of indicator values per candle, with None where there is not enough history."""
    close = pd.Series([float(c.close) for c in candles], dtype="float64")
    bands = ind.bollinger(close)
    macd = ind.macd(close)
    frame = pd.DataFrame(
        {
            "ema9": ind.ema(close, 9),
            "ema21": ind.ema(close, 21),
            "ema50": ind.ema(close, 50),
            "bb_upper": bands["upper"],
            "bb_mid": bands["mid"],
            "bb_lower": bands["lower"],
            "rsi14": ind.rsi(close, 14),
            "macd": macd["macd"],
            "macd_signal": macd["signal"],
            "macd_hist": macd["hist"],
        }
    )
    # JSON has no NaN, so warm-up values become null.
    return frame.astype(object).where(frame.notna(), None).to_dict("records")
