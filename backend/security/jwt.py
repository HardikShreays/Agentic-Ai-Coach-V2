from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt as jose_jwt


def _get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")
    return secret


def _get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


def _get_expiry() -> timedelta:
    minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days
    return timedelta(minutes=minutes)


def create_access_token(*, user_id: str, email: str, extra: Optional[dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + _get_expiry()).timestamp()),
    }
    if extra:
        payload.update(extra)
    token = jose_jwt.encode(payload, _get_jwt_secret(), algorithm=_get_jwt_algorithm())
    return token


def verify_access_token(token: str) -> dict[str, Any]:
    payload = jose_jwt.decode(token, _get_jwt_secret(), algorithms=[_get_jwt_algorithm()])
    return payload

