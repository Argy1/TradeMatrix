"""Alert SQL against the REAL database, inside a transaction that is rolled back.

Run on purpose with: uv run pytest -m db
An alert needs a user. The tests add a throwaway user inside the rolled-back transaction; if
the database role may not do that, they borrow the id of an existing user (still rolled back).
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.evaluate import evaluate_price_alerts, evaluate_signal_alerts
from app.api import alerts as api
from app.api.alerts import MAX_ALERTS, AlertIn
from app.data import repo

pytestmark = pytest.mark.db
T0 = datetime(2001, 1, 1, tzinfo=UTC)


async def a_user(session: AsyncSession) -> UUID:
    try:
        async with session.begin_nested():
            created = await session.execute(
                text("insert into auth.users (id) values (gen_random_uuid()) returning id")
            )
            return created.scalar_one()
    except Exception:
        existing = (await session.execute(text("select id from auth.users limit 1"))).first()
        if existing is None:
            pytest.skip("no user available to attach test alerts to")
        return existing[0]


async def model_id(session: AsyncSession, asset_id: int) -> int:
    created = await session.execute(
        text(
            "insert into model_versions (asset_id, timeframe, train_start, train_end, "
            "artifact_path) values (:a, '1h', :t, :t, 'test/none.joblib') returning id"
        ),
        {"a": asset_id, "t": T0},
    )
    return created.scalar_one()


async def add_signal(
    session: AsyncSession, asset_id: int, model: int, target: datetime, label: str, p_up: float
) -> None:
    await session.execute(
        text(
            "insert into predictions (asset_id, timeframe, base_open_time, target_open_time, "
            "base_close, p_ml, p_up, label, model_version_id, features) "
            "values (:a, '1h', :base, :target, 100, :p, :p, :label, :m, '{}')"
        ),
        {
            "a": asset_id,
            "base": target - timedelta(hours=1),
            "target": target,
            "p": p_up,
            "label": label,
            "m": model,
        },
    )


async def my_notifications(session: AsyncSession, user_id: UUID) -> list[str]:
    return [n.title for n in (await api.list_notifications(session, user_id, 50)).items]


class Prices:
    """Stands in for the exchange: returns the queued prices, one per check."""

    def __init__(self, *prices: str) -> None:
        self.prices = [Decimal(p) for p in prices]
        self.calls = 0

    async def get_last_price(self, _symbol: str) -> Decimal:
        self.calls += 1
        return self.prices.pop(0)


async def test_rules_are_stored_per_user_and_capped(session: AsyncSession) -> None:
    user, btc = await a_user(session), await repo.get_asset(session, "BTC")
    before = len(await api.list_alerts(session, user))
    rule = AlertIn(symbol="BTC", type="prob_above", timeframe="1h", threshold=Decimal("0.6"))
    alert_id = await api.create_alert(session, user, btc.id, rule)

    stored = await api.get_alert(session, user, alert_id)
    assert (stored.symbol, stored.type, stored.timeframe, stored.threshold) == (
        "BTC", "prob_above", "1h", "0.6",
    )  # fmt: skip
    assert stored.active and stored.cooldown_minutes == 60 and stored.last_triggered_at is None

    await api.update_alert(session, user, alert_id, {"active": False})
    changed = await api.get_alert(session, user, alert_id)
    assert changed.active is False and changed.threshold == "0.6"  # only what was sent changed

    # Another user's id finds nothing, even with the right alert id.
    stranger = UUID("00000000-0000-4000-8000-000000000001")
    assert await api.get_alert(session, stranger, alert_id) is None
    assert await api.delete_alert(session, stranger, alert_id) is False

    for _ in range(MAX_ALERTS - before - 1):
        assert await api.create_alert(session, user, btc.id, rule) is not None
    assert await api.create_alert(session, user, btc.id, rule) is None  # the cap holds
    assert await api.delete_alert(session, user, alert_id) is True
    assert len(await api.list_alerts(session, user)) == MAX_ALERTS - 1


async def test_signal_alerts_fire_once_per_new_signal(session: AsyncSession) -> None:
    user, btc = await a_user(session), await repo.get_asset(session, "BTC")
    model = await model_id(session, btc.id)
    # Far in the future, so these are "the newest predictions" for BTC 1h in this transaction.
    hour = datetime(2099, 1, 1, tzinfo=UTC)
    await add_signal(session, btc.id, model, hour, "neutral", 0.52)  # exists before the rules

    change = await api.create_alert(
        session, user, btc.id, AlertIn(symbol="BTC", type="signal_change", timeframe="1h")
    )
    above = await api.create_alert(
        session, user, btc.id,
        AlertIn(symbol="BTC", type="prob_above", timeframe="1h", threshold=Decimal("0.6"),
                cooldown_minutes=120),
    )  # fmt: skip
    seen_before = len(await my_notifications(session, user))

    # A signal that was already there when the rule was made never fires it.
    await evaluate_signal_alerts(session)
    assert len(await my_notifications(session, user)) == seen_before

    await add_signal(session, btc.id, model, hour + timedelta(hours=1), "up", 0.61)
    first = await evaluate_signal_alerts(session)
    again = await evaluate_signal_alerts(session)  # the job running twice
    assert first["fired"] == 2 and again["fired"] == 0
    titles = await my_notifications(session, user)
    assert "BTC 1h signal changed to Up" in titles
    assert "BTC 1h: chance of Up is 61.0%" in titles
    # The rule remembers the candle that fired it.
    assert (await api.get_alert(session, user, change)).last_triggered_at == hour + timedelta(
        hours=1
    )

    # Next candle, still Up at 62%: no change, and the 120-minute cooldown holds the other rule.
    await add_signal(session, btc.id, model, hour + timedelta(hours=2), "up", 0.62)
    assert (await evaluate_signal_alerts(session))["fired"] == 0
    # Two hours after it fired, the probability rule may fire again.
    await add_signal(session, btc.id, model, hour + timedelta(hours=3), "up", 0.63)
    assert (await evaluate_signal_alerts(session))["fired"] == 1
    assert (await api.get_alert(session, user, above)).last_triggered_at == hour + timedelta(
        hours=3
    )

    # A paused rule is skipped.
    await api.update_alert(session, user, change, {"active": False})
    await add_signal(session, btc.id, model, hour + timedelta(hours=4), "down", 0.38)
    assert (await evaluate_signal_alerts(session))["fired"] == 0


async def test_price_alert_fires_on_the_crossing_and_notifications_can_be_read(
    session: AsyncSession,
) -> None:
    user, btc = await a_user(session), await repo.get_asset(session, "BTC")
    await api.create_alert(
        session, user, btc.id,
        AlertIn(symbol="BTC", type="price_above", threshold=Decimal("85000"), cooldown_minutes=30),
    )  # fmt: skip
    seen_before = len(await my_notifications(session, user))
    prices = Prices("84900", "85010.5", "85300", "84000", "85100")
    memory: dict[str, Decimal] = {}
    now = datetime(2099, 1, 1, tzinfo=UTC)

    async def check(minutes: int) -> int:
        result = await evaluate_price_alerts(
            session, prices, memory, now + timedelta(minutes=minutes)
        )
        assert result["errors"] == []
        return result["fired"]

    assert await check(0) == 0  # first look: only remembers 84,900
    assert await check(1) == 1  # 84,900 -> 85,010.5 crosses the level
    assert await check(2) == 0  # stays above: no second notification
    assert await check(3) == 0  # falls back below
    assert await check(4) == 0  # crosses again, but inside the 30-minute cooldown
    assert memory == {"BTC": Decimal("85100")}

    listing = await api.list_notifications(session, user, 50)
    assert len(listing.items) == seen_before + 1
    newest = listing.items[0]
    assert newest.title == "BTC crossed above $85,000" and "$85,010.5" in newest.body
    assert newest.data["kind"] == "price" and newest.read_at is None

    read = await api.mark_read(session, user, newest.id)
    assert read.read_at is not None
    assert (await api.mark_read(session, user, newest.id)).read_at == read.read_at  # idempotent
    stranger = UUID("00000000-0000-4000-8000-000000000001")
    assert await api.mark_read(session, stranger, newest.id) is None
    assert (await api.list_notifications(session, user, 50)).unread == listing.unread - 1


async def test_no_price_alerts_means_no_price_request(session: AsyncSession) -> None:
    await session.execute(
        text("update alerts set active = false where type in ('price_above', 'price_below')")
    )  # rolled back with the rest of the test
    prices, memory = Prices(), {"BTC": Decimal("1")}
    result = await evaluate_price_alerts(session, prices, memory)
    assert result == {"checked": 0, "fired": 0, "errors": []}
    assert prices.calls == 0 and memory == {}  # nothing fetched, nothing remembered
