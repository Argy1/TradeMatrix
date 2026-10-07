"""Check the active alerts against stored data and write notifications (worker only).

Signal alerts are checked right after new predictions are stored; price alerts every minute.
Both are safe to run twice: `alerts.last_triggered_at` remembers the event that fired, and
the same event can never fire the same rule again.
"""

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.rules import (
    Signal,
    cooled_down,
    price_alert_fires,
    price_notification,
    signal_alert_fires,
    signal_notification,
)
from app.data.exchanges import ExchangeClient

# Each active signal alert with the newest prediction of its coin and candle size, and the
# label of the one before. Two guards keep an alert from firing on something old:
#   * the prediction was made after the alert was created, and
#   * its candle is later than the event that fired this alert last time.
_DUE_SIGNAL_ALERTS = text(
    """
    select al.id, al.user_id, a.symbol, al.timeframe, al.type, al.threshold,
           al.cooldown_minutes, al.last_triggered_at,
           latest.label, latest.p_up, latest.target_open_time, previous.label as previous_label
    from alerts al
    join assets a on a.id = al.asset_id and a.active
    join lateral (
      select p.label, p.p_up, p.target_open_time, p.created_at
      from predictions p
      where p.asset_id = al.asset_id and p.timeframe = al.timeframe
      order by p.target_open_time desc limit 1
    ) latest on true
    left join lateral (
      select p.label from predictions p
      where p.asset_id = al.asset_id and p.timeframe = al.timeframe
        and p.target_open_time < latest.target_open_time
      order by p.target_open_time desc limit 1
    ) previous on true
    where al.active
      and al.type in ('signal_change', 'prob_above', 'prob_below')
      and latest.created_at >= al.created_at
      and (al.last_triggered_at is null or latest.target_open_time > al.last_triggered_at)
    order by al.created_at
    """
)

_ACTIVE_PRICE_ALERTS = text(
    """
    select al.id, al.user_id, a.symbol, a.exchange_symbol, al.type, al.threshold,
           al.cooldown_minutes, al.last_triggered_at
    from alerts al
    join assets a on a.id = al.asset_id and a.active
    where al.active and al.type in ('price_above', 'price_below') and al.threshold is not null
    order by al.created_at
    """
)


async def _notify(
    session: AsyncSession,
    alert_id: UUID,
    user_id: UUID,
    message: tuple[str, str, dict],
    event_time: datetime,
) -> None:
    title, body, data = message
    await session.execute(
        text(
            "insert into notifications (user_id, alert_id, title, body, data) "
            "values (:user_id, :alert_id, :title, :body, cast(:data as jsonb))"
        ),
        {
            "user_id": user_id,
            "alert_id": alert_id,
            "title": title,
            "body": body,
            "data": json.dumps(data),
        },
    )
    await session.execute(
        text("update alerts set last_triggered_at = :event_time where id = :id"),
        {"event_time": event_time, "id": alert_id},
    )


async def evaluate_signal_alerts(session: AsyncSession) -> dict:
    """Fire signal alerts for the newest predictions. For these alerts `last_triggered_at`
    holds the open time of the candle whose signal fired, so the cooldown counts in candles
    (60 minutes = every 1h signal) and is not thrown off by a job that runs a few seconds late.
    """
    rows = (await session.execute(_DUE_SIGNAL_ALERTS)).all()
    fired = 0
    for row in rows:
        signal = Signal(row.label, float(row.p_up), row.target_open_time, row.previous_label)
        if not signal_alert_fires(row.type, row.threshold, signal):
            continue
        if not cooled_down(row.last_triggered_at, signal.target_open_time, row.cooldown_minutes):
            continue
        message = signal_notification(row.symbol, row.timeframe, row.type, row.threshold, signal)
        await _notify(session, row.id, row.user_id, message, signal.target_open_time)
        fired += 1
    return {"checked": len(rows), "fired": fired}


async def evaluate_price_alerts(
    session: AsyncSession,
    client: ExchangeClient,
    last_prices: dict[str, Decimal],
    now: datetime | None = None,
) -> dict:
    """Fire price alerts whose level was crossed since the previous check.

    `last_prices` is kept by the worker between runs (coin -> price seen a minute ago). When
    nobody has a price alert, no price is fetched at all.
    """
    now = now or datetime.now(UTC)
    rows = (await session.execute(_ACTIVE_PRICE_ALERTS)).all()
    wanted = {row.symbol: row.exchange_symbol for row in rows}
    current: dict[str, Decimal] = {}
    errors: list[str] = []
    for symbol, exchange_symbol in wanted.items():
        try:
            current[symbol] = await client.get_last_price(exchange_symbol)
        except Exception as exc:  # one coin without a price must not block the others
            errors.append(f"{symbol}: {type(exc).__name__}: {exc}"[:160])
    fired = 0
    for row in rows:
        if row.symbol not in current:
            continue
        previous, price = last_prices.get(row.symbol), current[row.symbol]
        if not price_alert_fires(row.type, row.threshold, previous, price):
            continue
        if not cooled_down(row.last_triggered_at, now, row.cooldown_minutes):
            continue
        message = price_notification(row.symbol, row.type, row.threshold, price)
        await _notify(session, row.id, row.user_id, message, now)
        fired += 1
    # Remember only coins that are still watched. A coin whose price could not be read keeps
    # its older price, so a crossing during that gap is still seen at the next check.
    remembered = {s: p for s, p in last_prices.items() if s in wanted} | current
    last_prices.clear()
    last_prices.update(remembered)
    return {"checked": len(rows), "fired": fired, "errors": errors}
