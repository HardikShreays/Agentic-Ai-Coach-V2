from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def _get_mongo_url() -> Optional[str]:
    url = os.getenv("MONGO_URL")
    return url.strip() if url else None


def _get_db_name() -> str:
    return os.getenv("MONGO_DB_NAME", "acadpipeline")


def create_mongo_client() -> AsyncIOMotorClient:
    mongo_url = _get_mongo_url()
    if not mongo_url:
        raise RuntimeError("MONGO_URL is not set")
    return AsyncIOMotorClient(mongo_url)


def get_database(client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    return client[_get_db_name()]

