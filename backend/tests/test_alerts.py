"""Alerts: when a rule fires, what the notification says, and the API around the rules."""

import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.alerts.rules import (
    DISCLAIMER_SHORT,
    Signal,
    cooled_down,
    money,
    price_alert_fires,
    price_notification,
    signal_alert_fires,
    signal_notification,
)
from app.api import alerts, v1
from app.api.alerts import MAX_ALERTS, AlertOut, NotificationOut, NotificationsOut
from app.api.auth import TokenVerifier, get_token_verifier
from app.api.main import app
from app.data.repo import Asset

T = datetime(2026, 10, 7, 14, 0, tzinfo=UTC)


def signal(label: str = "up", p_up: float = 0.61, previous: str | None = "neutral") -> Signal:
    return Signal(label, p_up, T, previous)


# ---- when a rule fires ----


def test_signal_change_fires_only_when_the_label_differs() -> None:
    assert signal_alert_fires("signal_change", None, signal("up", previous="neutral"))
    assert signal_alert_fires("signal_change", None, signal("down", 0.4, previous="up"))
    assert not signal_alert_fires("signal_change", None, signal("up", previous="up"))
    # The very first prediction of a coin has nothing before it: that is not a "change".
    assert not signal_alert_fires("signal_change", None, signal("up", previous=None))


def test_probability_alerts_compare_p_up_with_the_threshold() -> None:
    assert signal_alert_fires("prob_above", Decimal("0.60"), signal(p_up=0.61))
    assert signal_alert_fires("prob_above", Decimal("0.61"), signal(p_up=0.61))  # "at or above"
    assert not signal_alert_fires("prob_above", Decimal("0.62"), signal(p_up=0.61))
    assert signal_alert_fires("prob_below", Decimal("0.40"), signal("down", 0.38))
    assert not signal_alert_fires("prob_below", Decimal("0.40"), signal("neutral", 0.48))
    assert not signal_alert_fires("prob_above", None, signal(p_up=0.99))  # no threshold, no alert
    assert not signal_alert_fires("price_above", Decimal("1"), signal())  # not a signal rule


def test_price_alerts_fire_on_a_crossing_not_on_a_level() -> None:
    level = Decimal("85000")
    assert price_alert_fires("price_above", level, Decimal("84990"), Decimal("85010"))
    assert price_alert_fires("price_above", level, Decimal("84990"), Decimal("85000"))  # touches
    # Already above a minute ago: no new crossing, so no repeat notification.
    assert not price_alert_fires("price_above", level, Decimal("85010"), Decimal("85200"))
    assert not price_alert_fires("price_above", level, Decimal("84000"), Decimal("84990"))
    assert price_alert_fires("price_below", level, Decimal("85010"), Decimal("84990"))
    assert not price_alert_fires("price_below", level, Decimal("84990"), Decimal("84000"))
    # First check after a restart: no earlier price, so no crossing can be claimed.
    assert not price_alert_fires("price_above", level, None, Decimal("90000"))


def test_cooldown_allows_one_notification_per_period() -> None:
    assert cooled_down(None, T, 60)
    assert cooled_down(T - timedelta(minutes=60), T, 60)  # the next 1h candle is allowed
    assert not cooled_down(T - timedelta(minutes=59), T, 60)
    assert not cooled_down(T - timedelta(hours=1), T, 240)


# ---- what the notification says ----


def test_signal_change_notification_matches_the_signal_card() -> None:
    title, body, data = signal_notification("BTC", "1h", "signal_change", None, signal())
    assert title == "BTC 1h signal changed to Up"
    assert body == (
        "It was Neutral before. 61.0% chance the next 1 hour candle closes higher. "
        "Not financial advice. Estimates only."
    )
    assert data["label"] == "up" and data["p_up"] == 0.61 and data["previous_label"] == "neutral"
    assert data["target_open_time"] == "2026-10-07T14:00:00+00:00"


def test_down_and_neutral_wording() -> None:
    _, down, _ = signal_notification("ETH", "4h", "signal_change", None, signal("down", 0.38, "up"))
    assert "62.0% chance the next 4 hour candle closes lower." in down  # shows the Down chance
    _, flat, _ = signal_notification("ETH", "1d", "signal_change", None, signal("neutral", 0.52))
    assert "Up 52.0% versus down 48.0%: too close to call." in flat


def test_probability_notification_names_the_rule() -> None:
    title, body, _ = signal_notification("SOL", "1h", "prob_above", Decimal("0.6"), signal())
    assert title == "SOL 1h: chance of Up is 61.0%"
    assert body.startswith("Your alert: at or above 60%. Signal: Up.")
    _, below, _ = signal_notification(
        "SOL", "1h", "prob_below", Decimal("0.4"), signal("down", 0.38)
    )
    assert below.startswith("Your alert: at or below 40%. Signal: Down.")


def test_price_notification_is_exact_and_not_called_a_signal() -> None:
    title, body, data = price_notification(
        "BTC", "price_above", Decimal("85000.00"), Decimal("85012.30000000")
    )
    assert title == "BTC crossed above $85,000"
    assert body == f"Last price $85,012.3. This is a price alert, not a signal. {DISCLAIMER_SHORT}"
    assert data == {
        "kind": "price", "symbol": "BTC", "type": "price_above", "threshold": "85000",
        "price": "85012.3",
    }  # fmt: skip
    assert money(Decimal("0.00001234")) == "$0.00001234"  # small coins keep every digit


def test_every_notification_carries_the_disclaimer() -> None:
    for alert_type, threshold in [("signal_change", None), ("prob_above", Decimal("0.6"))]:
        _, body, _ = signal_notification("BTC", "1h", alert_type, threshold, signal())
        assert body.endswith(DISCLAIMER_SHORT)
    assert DISCLAIMER_SHORT == "Not financial advice. Estimates only."  # docs/06, exact text


# ---- the API ----

KEY = ec.generate_private_key(ec.SECP256R1())
ISSUER = "https://example.supabase.co/auth/v1"


def token(user_id: str) -> dict:
    claims = {"sub": user_id, "aud": "authenticated", "iss": ISSUER, "exp": int(time.time()) + 600}
    return {"Authorization": f"Bearer {jwt.encode(claims, KEY, algorithm='ES256')}"}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    """The real routes, validation and auth; only the SQL functions are replaced by dicts."""
    rules: dict[UUID, tuple[UUID, AlertOut]] = {}  # alert id -> (owner, alert)
    notes: dict[int, tuple[UUID, NotificationOut]] = {}

    async def fake_db():
        yield None

    async def get_asset(_session, symbol):
        return Asset(1, "BTC", "Bitcoin", "BTCUSDT") if symbol == "BTC" else None

    async def list_alerts(_session, user_id):
        return [alert for owner, alert in rules.values() if owner == user_id]

    async def get_alert(_session, user_id, alert_id):
        owner, alert = rules.get(alert_id, (None, None))
        return alert if owner == user_id else None

    async def create_alert(_session, user_id, _asset_id, body):
        if len(await list_alerts(None, user_id)) >= MAX_ALERTS:
            return None
        alert = AlertOut(
            id=uuid4(), symbol=body.symbol.upper(), type=body.type, timeframe=body.timeframe,
            threshold=None if body.threshold is None else format(body.threshold.normalize(), "f"),
            cooldown_minutes=body.cooldown_minutes, active=True, last_triggered_at=None,
            created_at=T,
        )  # fmt: skip
        rules[alert.id] = (user_id, alert)
        return alert.id

    async def update_alert(_session, user_id, alert_id, changes):
        owner, alert = rules[alert_id]
        if "threshold" in changes:
            changes = changes | {"threshold": format(changes["threshold"].normalize(), "f")}
        rules[alert_id] = (owner, alert.model_copy(update=changes))

    async def delete_alert(_session, user_id, alert_id):
        if rules.get(alert_id, (None,))[0] != user_id:
            return False
        del rules[alert_id]
        return True

    async def list_notifications(_session, user_id, limit):
        mine = [note for owner, note in notes.values() if owner == user_id][:limit]
        return NotificationsOut(items=mine, unread=sum(n.read_at is None for n in mine))

    async def mark_read(_session, user_id, notification_id):
        owner, note = notes.get(notification_id, (None, None))
        if owner != user_id:
            return None
        notes[notification_id] = (owner, note.model_copy(update={"read_at": T}))
        return notes[notification_id][1]

    monkeypatch.setattr(alerts.repo, "get_asset", get_asset)
    for name, fake in [
        ("list_alerts", list_alerts), ("get_alert", get_alert), ("create_alert", create_alert),
        ("update_alert", update_alert), ("delete_alert", delete_alert),
        ("list_notifications", list_notifications), ("mark_read", mark_read),
    ]:  # fmt: skip
        monkeypatch.setattr(alerts, name, fake)
    verifier = TokenVerifier(issuer=ISSUER, key_resolver=lambda _t: (KEY.public_key(), ["ES256"]))
    app.dependency_overrides[get_token_verifier] = lambda: verifier
    app.dependency_overrides[v1.get_db] = fake_db
    yield TestClient(app), notes
    app.dependency_overrides.clear()


SIGNAL_RULE = {"symbol": "btc", "type": "signal_change", "timeframe": "1h"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/v1/alerts"),
        ("post", "/v1/alerts"),
        ("patch", f"/v1/alerts/{uuid4()}"),
        ("delete", f"/v1/alerts/{uuid4()}"),
        ("get", "/v1/notifications"),
        ("post", "/v1/notifications/1/read"),
    ],
)
def test_login_is_required(client, method: str, path: str) -> None:
    response = getattr(client[0], method)(path)
    assert response.status_code == 401 and response.json()["error"]["code"] == "unauthorized"


def test_create_list_change_and_delete_a_rule(client) -> None:
    http, me = client[0], token(str(uuid4()))
    created = http.post("/v1/alerts", json=SIGNAL_RULE, headers=me)
    assert created.status_code == 201
    rule = created.json()
    assert (rule["symbol"], rule["type"], rule["timeframe"]) == ("BTC", "signal_change", "1h")
    assert rule["threshold"] is None and rule["cooldown_minutes"] == 60 and rule["active"] is True

    price = http.post(
        "/v1/alerts",
        json={"symbol": "BTC", "type": "price_above", "threshold": "85000.50"},
        headers=me,
    ).json()
    assert price["threshold"] == "85000.5" and price["timeframe"] is None  # a string, exact

    listed = http.get("/v1/alerts", headers=me).json()
    assert len(listed["items"]) == 2 and listed["max_alerts"] == MAX_ALERTS

    paused = http.patch(f"/v1/alerts/{rule['id']}", json={"active": False}, headers=me).json()
    assert paused["active"] is False and paused["cooldown_minutes"] == 60  # only what was sent
    moved = http.patch(f"/v1/alerts/{price['id']}", json={"threshold": "90000"}, headers=me)
    assert moved.json()["threshold"] == "90000"

    left = http.delete(f"/v1/alerts/{rule['id']}", headers=me).json()
    assert [item["id"] for item in left["items"]] == [price["id"]]


def test_another_users_rule_looks_like_it_does_not_exist(client) -> None:
    http, alice, bob = client[0], token(str(uuid4())), token(str(uuid4()))
    rule_id = http.post("/v1/alerts", json=SIGNAL_RULE, headers=alice).json()["id"]
    assert http.get("/v1/alerts", headers=bob).json()["items"] == []
    assert (
        http.patch(f"/v1/alerts/{rule_id}", json={"active": False}, headers=bob).status_code == 404
    )
    assert http.delete(f"/v1/alerts/{rule_id}", headers=bob).status_code == 404
    assert len(http.get("/v1/alerts", headers=alice).json()["items"]) == 1  # untouched


@pytest.mark.parametrize(
    "body",
    [
        {"symbol": "BTC", "type": "signal_change"},  # signal rule without a candle size
        {"symbol": "BTC", "type": "signal_change", "timeframe": "1h", "threshold": "0.6"},
        {"symbol": "BTC", "type": "prob_above", "timeframe": "1h"},  # no threshold
        {"symbol": "BTC", "type": "prob_above", "timeframe": "1h", "threshold": "1.5"},
        {"symbol": "BTC", "type": "prob_below", "timeframe": "1h", "threshold": "0"},
        {"symbol": "BTC", "type": "price_above", "threshold": "-5"},
        {"symbol": "BTC", "type": "price_above", "timeframe": "1h", "threshold": "85000"},
        {"symbol": "BTC", "type": "price_above"},
        {"symbol": "BTC", "type": "buy_now", "threshold": "1"},  # not a rule we offer
        {"symbol": "BTC", "type": "signal_change", "timeframe": "15m"},
        {"symbol": "BTC", "type": "signal_change", "timeframe": "1h", "cooldown_minutes": 0},
    ],
)
def test_rules_that_make_no_sense_are_refused(client, body: dict) -> None:
    response = client[0].post("/v1/alerts", json=body, headers=token(str(uuid4())))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_unknown_coin_limit_and_bad_change(client) -> None:
    http, me = client[0], token(str(uuid4()))
    unknown = http.post("/v1/alerts", json=SIGNAL_RULE | {"symbol": "NOTACOIN"}, headers=me)
    assert unknown.status_code == 404
    for _ in range(MAX_ALERTS):
        assert http.post("/v1/alerts", json=SIGNAL_RULE, headers=me).status_code == 201
    over = http.post("/v1/alerts", json=SIGNAL_RULE, headers=me)
    assert over.status_code == 409 and over.json()["error"]["code"] == "alert_limit"
    rule_id = http.get("/v1/alerts", headers=me).json()["items"][0]["id"]
    # A signal_change rule has no threshold, so giving it one is refused.
    bad = http.patch(f"/v1/alerts/{rule_id}", json={"threshold": "0.6"}, headers=me)
    assert bad.status_code == 422


def test_notifications_are_private_and_can_be_marked_read(client) -> None:
    http, notes = client
    alice_id, bob = uuid4(), token(str(uuid4()))
    alice = token(str(alice_id))
    notes[7] = (
        alice_id,
        NotificationOut(
            id=7, title="BTC 1h signal changed to Up", body="...", data={"kind": "signal"},
            created_at=T, read_at=None,
        ),
    )  # fmt: skip
    mine = http.get("/v1/notifications", headers=alice).json()
    assert mine["unread"] == 1 and mine["items"][0]["title"] == "BTC 1h signal changed to Up"
    assert http.get("/v1/notifications", headers=bob).json() == {"items": [], "unread": 0}
    assert http.post("/v1/notifications/7/read", headers=bob).status_code == 404
    read = http.post("/v1/notifications/7/read", headers=alice).json()
    assert read["read_at"] is not None
    assert http.get("/v1/notifications", headers=alice).json()["unread"] == 0
    assert http.get("/v1/notifications?limit=101", headers=alice).status_code == 422
