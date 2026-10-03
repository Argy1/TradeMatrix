"""Watchlist endpoints: login required, and every call is scoped to the token's user."""

import time
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.api import account, v1
from app.api.auth import TokenVerifier, get_token_verifier
from app.api.main import app
from app.data.repo import Asset

KEY = ec.generate_private_key(ec.SECP256R1())
ISSUER = "https://example.supabase.co/auth/v1"


def token(user_id: str) -> dict:
    claims = {"sub": user_id, "aud": "authenticated", "iss": ISSUER, "exp": int(time.time()) + 600}
    return {"Authorization": f"Bearer {jwt.encode(claims, KEY, algorithm='ES256')}"}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    lists: dict = {}  # user id -> list of asset ids, standing in for the watchlists table

    async def fake_db():
        yield None

    async def get_asset(_session, symbol):
        ids = {"BTC": 1, "ETH": 2}
        return Asset(ids[symbol], symbol, symbol, symbol + "USDT") if symbol in ids else None

    async def symbols(_session, user_id):
        names = {1: "BTC", 2: "ETH"}
        return [names[a] for a in lists.get(user_id, [])]

    async def add(_session, user_id, asset_id):
        if asset_id not in lists.setdefault(user_id, []):
            lists[user_id].append(asset_id)

    async def remove(_session, user_id, asset_id):
        lists.get(user_id, []).remove(asset_id) if asset_id in lists.get(user_id, []) else None

    monkeypatch.setattr(account.repo, "get_asset", get_asset)
    monkeypatch.setattr(account, "watchlist_symbols", symbols)
    monkeypatch.setattr(account, "add_to_watchlist", add)
    monkeypatch.setattr(account, "remove_from_watchlist", remove)
    verifier = TokenVerifier(issuer=ISSUER, key_resolver=lambda _t: (KEY.public_key(), ["ES256"]))
    app.dependency_overrides[get_token_verifier] = lambda: verifier
    app.dependency_overrides[v1.get_db] = fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_login_is_required(client: TestClient, method: str) -> None:
    path = "/v1/watchlist" if method == "get" else "/v1/watchlist/BTC"
    response = getattr(client, method)(path)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_each_user_sees_only_their_own_list(client: TestClient) -> None:
    alice, bob = str(uuid4()), str(uuid4())
    assert client.put("/v1/watchlist/btc", headers=token(alice)).json() == {"symbols": ["BTC"]}
    assert client.put("/v1/watchlist/BTC", headers=token(alice)).json() == {"symbols": ["BTC"]}
    assert client.put("/v1/watchlist/ETH", headers=token(alice)).json() == {
        "symbols": ["BTC", "ETH"]
    }
    assert client.get("/v1/watchlist", headers=token(bob)).json() == {"symbols": []}
    assert client.delete("/v1/watchlist/BTC", headers=token(alice)).json() == {"symbols": ["ETH"]}


def test_unknown_coin(client: TestClient) -> None:
    response = client.put("/v1/watchlist/DOGE", headers=token(str(uuid4())))
    assert response.status_code == 404
