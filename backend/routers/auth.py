from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

from security.jwt import create_access_token
from security.passwords import hash_password, verify_password
from security.deps import get_current_user


router = APIRouter()


COOKIE_NAME_DEFAULT = "acadpipeline_token"


def _cookie_name() -> str:
    return os.getenv("COOKIE_NAME", COOKIE_NAME_DEFAULT)


def _cookie_max_age_seconds() -> int:
    minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))
    return minutes * 60


def _cookie_secure_flag() -> bool:
    # In local dev this should stay false; in production set COOKIE_SECURE=true
    return os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}


def _cookie_samesite() -> str:
    """
    For cross-site frontend/backend domains (Vercel + Render), use SameSite=None with secure cookies.
    """
    value = os.getenv("COOKIE_SAMESITE", "lax").strip().lower()
    if value not in {"lax", "strict", "none"}:
        return "lax"
    return value


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthMeResponse(BaseModel):
    user_id: str
    email: str


@router.post("/auth/signup", response_model=AuthMeResponse)
async def signup(req: SignupRequest, response: Response, request: Request) -> AuthMeResponse:
    db = request.app.state.db
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")

    existing = await db["users"].find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    pw_hash = hash_password(req.password)
    doc = {"email": req.email, "password_hash": pw_hash}
    result = await db["users"].insert_one(doc)

    user_id = str(result.inserted_id)
    token = create_access_token(user_id=user_id, email=req.email)

    response.set_cookie(
        key=_cookie_name(),
        value=token,
        httponly=True,
        samesite=_cookie_samesite(),
        secure=_cookie_secure_flag(),
        max_age=_cookie_max_age_seconds(),
        path="/",
    )

    return AuthMeResponse(user_id=user_id, email=req.email)


@router.post("/auth/login", response_model=AuthMeResponse)
async def login(req: LoginRequest, response: Response, request: Request) -> AuthMeResponse:
    db = request.app.state.db
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")

    user = await db["users"].find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    password_hash = user.get("password_hash")
    if not password_hash or not verify_password(req.password, password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_id = str(user["_id"])
    token = create_access_token(user_id=user_id, email=req.email)
    response.set_cookie(
        key=_cookie_name(),
        value=token,
        httponly=True,
        samesite=_cookie_samesite(),
        secure=_cookie_secure_flag(),
        max_age=_cookie_max_age_seconds(),
        path="/",
    )

    return AuthMeResponse(user_id=user_id, email=req.email)


@router.post("/auth/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(key=_cookie_name(), path="/")
    return {"ok": True}


@router.get("/auth/me", response_model=AuthMeResponse)
async def me(user: dict = Depends(get_current_user)) -> AuthMeResponse:
    return AuthMeResponse(user_id=user["_id"], email=user["email"])

