"""JWT verification with fake tokens signed by a throwaway key (no Supabase needed)."""

import time
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth import CurrentUser, TokenVerifier, get_token_verifier
from app.api.errors import install_error_handlers

ISSUER = "https://example.supabase.co/auth/v1"
USER_ID = str(uuid4())

# Supabase signs with a private key and publishes the public half. We do the same here.
PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
OTHER_KEY = ec.generate_private_key(ec.SECP256R1())


def make_token(key=PRIVATE_KEY, **overrides) -> str:
    claims = {
        "sub": USER_ID,
        "email": "argy@example.com",
        "aud": "authenticated",
        "iss": ISSUER,
        "exp": int(time.time()) + 3600,
    }
    claims.update(overrides)
    claims = {name: value for name, value in claims.items() if value is not None}
    return jwt.encode(claims, key, algorithm="ES256")


@pytest.fixture
def verifier() -> TokenVerifier:
    return TokenVerifier(
        issuer=ISSUER, key_resolver=lambda _token: (PRIVATE_KEY.public_key(), ["ES256"])
    )


@pytest.fixture
def client(verifier: TokenVerifier) -> TestClient:
    app = FastAPI()
    install_error_handlers(app)
    app.dependency_overrides[get_token_verifier] = lambda: verifier

    @app.get("/me")
    def me(user: CurrentUser) -> dict:
        return {"user_id": str(user.user_id), "email": user.email}

    return TestClient(app)


def test_valid_token_returns_the_user(verifier: TokenVerifier) -> None:
    user = verifier.verify(make_token())
    assert str(user.user_id) == USER_ID
    assert user.email == "argy@example.com"


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(make_token(exp=int(time.time()) - 60), id="expired"),
        pytest.param(make_token(aud="anon"), id="wrong audience"),
        pytest.param(make_token(iss="https://evil.example/auth/v1"), id="wrong issuer"),
        pytest.param(make_token(key=OTHER_KEY), id="signed by another key"),
        pytest.param(make_token(sub=None), id="no user id"),
        pytest.param(make_token(sub="not-a-uuid"), id="user id is not a uuid"),
        pytest.param(make_token(exp=None), id="no expiry"),
        pytest.param("not.a.token", id="garbage"),
    ],
)
def test_bad_tokens_are_rejected(verifier: TokenVerifier, token: str) -> None:
    with pytest.raises(jwt.PyJWTError):
        verifier.verify(token)


def test_unsigned_token_is_rejected(verifier: TokenVerifier) -> None:
    # "alg: none" tokens have no signature at all. Accepting one would let anyone log in.
    claims = {"sub": USER_ID, "aud": "authenticated", "iss": ISSUER, "exp": int(time.time()) + 60}
    unsigned = jwt.encode(claims, key=None, algorithm="none")
    with pytest.raises(jwt.PyJWTError):
        verifier.verify(unsigned)


def test_hs256_secret_fallback() -> None:
    secret = "a-test-secret-that-is-long-enough-for-hs256"
    verifier = TokenVerifier(issuer=ISSUER, jwt_secret=secret)
    claims = {"sub": USER_ID, "aud": "authenticated", "iss": ISSUER, "exp": int(time.time()) + 60}
    assert str(verifier.verify(jwt.encode(claims, secret, algorithm="HS256")).user_id) == USER_ID
    with pytest.raises(jwt.PyJWTError):
        verifier.verify(jwt.encode(claims, "wrong-secret-wrong-secret-wrong-secret", "HS256"))


def test_unconfigured_verifier_rejects_everything() -> None:
    with pytest.raises(jwt.PyJWTError):
        TokenVerifier().verify(make_token())


def test_protected_route(client: TestClient) -> None:
    ok = client.get("/me", headers={"Authorization": f"Bearer {make_token()}"})
    assert ok.status_code == 200
    assert ok.json() == {"user_id": USER_ID, "email": "argy@example.com"}

    missing = client.get("/me")
    assert missing.status_code == 401
    assert missing.json() == {"error": {"code": "unauthorized", "message": "Missing bearer token"}}

    expired = make_token(exp=int(time.time()) - 60)
    invalid = client.get("/me", headers={"Authorization": f"Bearer {expired}"})
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_token"
