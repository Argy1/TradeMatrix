"""When an alert fires and what its notification says (docs/04 "Alert rule semantics").

Everything here is plain logic with no database, so each rule can be tested on its own.
Notifications are fixed templates filled with stored values: they always match what the app
shows, and they never contain free text from an AI model.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

SIGNAL_TYPES = ("signal_change", "prob_above", "prob_below")
PRICE_TYPES = ("price_above", "price_below")
ALERT_TYPES = SIGNAL_TYPES + PRICE_TYPES

# Exact short text from docs/06. It may only change with Argy's approval.
DISCLAIMER_SHORT = "Not financial advice. Estimates only."

_WORD = {"up": "Up", "down": "Down", "neutral": "Neutral"}
_TF_WORDS = {"1h": "1 hour", "4h": "4 hour", "1d": "1 day"}


@dataclass(frozen=True, slots=True)
class Signal:
    """The newest stored prediction for an alert's coin and candle size."""

    label: str
    p_up: float
    target_open_time: datetime
    previous_label: str | None  # label of the prediction before it; None if there is none


def cooled_down(last_triggered_at: datetime | None, event_time: datetime, minutes: int) -> bool:
    """At most one notification per rule per cooldown (docs/04)."""
    return last_triggered_at is None or event_time - last_triggered_at >= timedelta(minutes=minutes)


def signal_alert_fires(alert_type: str, threshold: Decimal | None, signal: Signal) -> bool:
    if alert_type == "signal_change":
        return signal.previous_label is not None and signal.label != signal.previous_label
    if threshold is None:
        return False
    if alert_type == "prob_above":
        return signal.p_up >= float(threshold)
    if alert_type == "prob_below":
        return signal.p_up <= float(threshold)
    return False


def price_alert_fires(
    alert_type: str, threshold: Decimal, previous: Decimal | None, current: Decimal
) -> bool:
    """True only when the price CROSSES the level between two checks.

    A price that simply sits above the level does not fire again and again. `previous` is
    None on the first check after the worker starts: without an earlier price there is no
    crossing to see, so nothing fires.
    """
    if previous is None:
        return False
    if alert_type == "price_above":
        return previous < threshold <= current
    if alert_type == "price_below":
        return previous > threshold >= current
    return False


def _chance(label: str, p_up: float, timeframe: str) -> str:
    """The same sentence shape the signal card uses (docs/08)."""
    candle = f"the next {_TF_WORDS[timeframe]} candle"
    if label == "up":
        return f"{p_up:.1%} chance {candle} closes higher."
    if label == "down":
        return f"{1 - p_up:.1%} chance {candle} closes lower."
    return f"Up {p_up:.1%} versus down {1 - p_up:.1%}: too close to call."


def money(value: Decimal) -> str:
    """Decimal('85000.50') -> '$85,000.5' (no float rounding, no exponent form)."""
    return f"${value.normalize():,f}"


def signal_notification(
    symbol: str, timeframe: str, alert_type: str, threshold: Decimal | None, signal: Signal
) -> tuple[str, str, dict]:
    """(title, body, data) for a signal alert. Every body ends with the disclaimer."""
    word = _WORD[signal.label]
    chance = _chance(signal.label, signal.p_up, timeframe)
    if alert_type == "signal_change":
        title = f"{symbol} {timeframe} signal changed to {word}"
        body = f"It was {_WORD[signal.previous_label or 'neutral']} before. {chance}"
    else:
        side = "at or above" if alert_type == "prob_above" else "at or below"
        title = f"{symbol} {timeframe}: chance of Up is {signal.p_up:.1%}"
        body = f"Your alert: {side} {float(threshold or 0):.0%}. Signal: {word}. {chance}"
    data = {
        "kind": "signal",
        "symbol": symbol,
        "timeframe": timeframe,
        "type": alert_type,
        "label": signal.label,
        "p_up": round(signal.p_up, 4),
        "previous_label": signal.previous_label,
        "target_open_time": signal.target_open_time.isoformat(),
    }
    return title, f"{body} {DISCLAIMER_SHORT}", data


def price_notification(
    symbol: str, alert_type: str, threshold: Decimal, price: Decimal
) -> tuple[str, str, dict]:
    direction = "above" if alert_type == "price_above" else "below"
    title = f"{symbol} crossed {direction} {money(threshold)}"
    body = f"Last price {money(price)}. This is a price alert, not a signal. {DISCLAIMER_SHORT}"
    data = {
        "kind": "price",
        "symbol": symbol,
        "type": alert_type,
        "threshold": format(threshold.normalize(), "f"),
        "price": format(price.normalize(), "f"),
    }
    return title, body, data
