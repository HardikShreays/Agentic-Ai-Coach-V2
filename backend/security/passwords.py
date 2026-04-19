from __future__ import annotations

import hashlib

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_input(password: str) -> str:
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) <= 72:
        return password
    return hashlib.sha256(pw_bytes).hexdigest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_bcrypt_input(password))


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(_bcrypt_input(password), password_hash)

