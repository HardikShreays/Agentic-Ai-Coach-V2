from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, Request
from bson import ObjectId

from security.jwt import verify_access_token


async def get_current_user(request: Request) -> dict:
    import os

    cookie_name = os.getenv("COOKIE_NAME", "acadpipeline_token")
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db = request.app.state.db
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"_id": str(user["_id"]), "email": user.get("email")}


async def get_optional_current_user(request: Request) -> Optional[dict]:
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

