"""Verify Supabase login tokens (JWT) for protected routes.

A JWT is a signed note from Supabase Auth saying "this is user X until time T". The API
never trusts the note's content until it has checked the signature, the expiry time, the
audience and the issuer (docs/06 security checklist).
"""

from collections.abc import Callable
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.api.errors import ApiError
from app.config import get_settings

# (key, allowed algorithms) for a given token
KeyResolver = Callable[[str], tuple[Any, list[str]]]


class AuthUser(BaseModel):
    user_id: UUID
    email: str | None = None


class TokenVerifier:
    def __init__(
        self,
        *,
        issuer: str = "",
        audience: str = "authenticated",
        jwks_url: str = "",
        jwt_secret: str = "",
        key_resolver: KeyResolver | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._jwt_secret = jwt_secret
        self._key_resolver = key_resolver
        # PyJWKClient downloads Supabase's public keys once and caches them.
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True) if jwks_url else None

    def _signing_key(self, token: str) -> tuple[Any, list[str]]:
        if self._key_resolver is not None:
            return self._key_resolver(token)
        if self._jwks is not None:
            # Preferred: asymmetric keys. The API only holds the public key.
            return self._jwks.get_signing_key_from_jwt(token).key, ["ES256", "RS256"]
        if self._jwt_secret:
            return self._jwt_secret, ["HS256"]  # legacy shared secret
        raise jwt.InvalidTokenError("token verification is not configured")

    def verify(self, token: str) -> AuthUser:
        """Return the user, or raise jwt.PyJWTError if the token cannot be trusted."""
        key, algorithms = self._signing_key(token)
        claims = jwt.decode(
            token,
            key,
            # Never take the algorithm from the token itself: that is a classic attack.
            algorithms=algorithms,
            audience=self._audience,
            issuer=self._issuer or None,
            leeway=10,  # seconds of clock difference we tolerate
            options={"require": ["exp", "sub", "aud"]},
        )
        try:
            return AuthUser(user_id=UUID(claims["sub"]), email=claims.get("email"))
        except ValueError as exc:
            raise jwt.InvalidTokenError("sub is not a user id") from exc


@lru_cache
def get_token_verifier() -> TokenVerifier:
    settings = get_settings()
    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else ""
    return TokenVerifier(
        issuer=issuer,
        jwks_url=settings.supabase_jwks_url,
        jwt_secret=settings.supabase_jwt_secret,
    )


_bearer = HTTPBearer(auto_error=False)


# A plain `def` (not async): FastAPI runs it in a worker thread, so the blocking
# download of the public keys cannot freeze the event loop.
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> AuthUser:
    if credentials is None:
        raise ApiError(401, "unauthorized", "Missing bearer token")
    try:
        return verifier.verify(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise ApiError(401, "invalid_token", "Invalid or expired token") from exc


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
