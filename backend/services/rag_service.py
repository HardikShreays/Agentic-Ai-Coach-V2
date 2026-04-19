from __future__ import annotations

import json
import os
from pathlib import Path
from functools import lru_cache
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

KB_COLLECTION = os.getenv("KB_COLLECTION", "acad_coach_kb")
KB_PERSIST_DIR = Path(os.getenv("KB_CHROMA_DIR", str(Path(__file__).resolve().parent.parent / "data" / "chroma")))
KB_SOURCE_JSON = Path(
    os.getenv(
        "KB_SOURCE_JSON",
        str(Path(__file__).resolve().parent.parent / "knowledge_base" / "seed_documents.json"),
    )
)
KB_EMBED_MODEL = os.getenv("KB_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _client() -> chromadb.PersistentClient:
    KB_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(KB_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


@lru_cache(maxsize=1)
def _collection() -> Collection:
    return _client().get_or_create_collection(
        name=KB_COLLECTION,
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=KB_EMBED_MODEL),
    )


def _chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    clean = " ".join((text or "").split())
    if not clean:
        return []
    if len(clean) <= chunk_size:
        return [clean]
    chunks: list[str] = []
    i = 0
    step = max(1, chunk_size - overlap)
    while i < len(clean):
        piece = clean[i : i + chunk_size].strip()
        if piece:
            chunks.append(piece)
        i += step
    return chunks


def load_seed_documents(path: Path | None = None) -> list[dict[str, Any]]:
    source = path or KB_SOURCE_JSON
    if not source.exists():
        return []
    with source.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    docs = payload.get("documents", [])
    return [d for d in docs if isinstance(d, dict) and isinstance(d.get("content"), str)]


def ingest_documents(documents: list[dict[str, Any]]) -> int:
    col = _collection()
    existing_ids = (col.get(include=[]).get("ids") or [])
    if existing_ids:
        col.delete(ids=existing_ids)
    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, Any]] = []
    for idx, d in enumerate(documents):
        title = str(d.get("title", f"doc_{idx}"))
        role = str(d.get("role", "general"))
        topic = str(d.get("topic", "general"))
        source = str(d.get("source", "internal"))
        pieces = _chunk_text(str(d.get("content", "")))
        for j, chunk in enumerate(pieces):
            ids.append(f"{idx}_{j}")
            docs.append(chunk)
            metas.append(
                {
                    "title": title,
                    "role": role,
                    "topic": topic,
                    "source": source,
                    "chunk_index": j,
                }
            )
    if ids:
        col.add(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def ingest_seed_knowledge_base() -> int:
    return ingest_documents(load_seed_documents())


def _build_where(role: str | None, topic: str | None) -> dict[str, Any] | None:
    filters: list[dict[str, Any]] = []
    if role:
        filters.append({"role": {"$eq": role}})
    if topic:
        filters.append({"topic": {"$eq": topic}})
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def retrieve_guidance_context(
    query: str,
    *,
    role: str | None = None,
    topic: str | None = None,
    k: int = 4,
) -> list[dict[str, Any]]:
    col = _collection()
    if col.count() == 0:
        return []
    where = _build_where(role, topic)
    result = col.query(
        query_texts=[query],
        n_results=max(1, min(k, 8)),
        where=where,
    )
    out: list[dict[str, Any]] = []
    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    dists = (result.get("distances") or [[]])[0]
    for i, txt in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        dist = dists[i] if i < len(dists) else None
        out.append(
            {
                "content": txt,
                "title": (meta or {}).get("title"),
                "source": (meta or {}).get("source"),
                "role": (meta or {}).get("role"),
                "topic": (meta or {}).get("topic"),
                "distance": dist,
            }
        )
    return out


def format_retrieval_context(items: list[dict[str, Any]]) -> str:
    if not items:
        return (
            "No knowledge base matches were found. Ask follow-up questions or suggest general guidance while "
            "stating that no indexed source matched strongly."
        )
    lines = ["Retrieved guidance context:"]
    for idx, it in enumerate(items, start=1):
        title = it.get("title") or "Untitled"
        source = it.get("source") or "unknown"
        snippet = str(it.get("content") or "").strip().replace("\n", " ")
        lines.append(f"{idx}. [{title}] ({source}) {snippet[:320]}")
    return "\n".join(lines)
