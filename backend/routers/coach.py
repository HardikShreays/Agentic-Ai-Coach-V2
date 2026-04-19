from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from models.schemas import (
    CoachRequest,
    CoachResponse,
    PredictRequest,
    PredictResponse,
    RoadmapRequest,
    SessionContext,
)
from services.coach_agent import run_coach_agent_sync
from services.prompt_builder import build_coach_agent_system_prompt
from security.deps import get_optional_current_user


router = APIRouter()

def _doc_to_session_context(doc: dict | None) -> SessionContext | None:
    if not doc:
        return None
    return SessionContext(
        predicted_score=doc.get("predicted_score"),
        grade=doc.get("grade"),
        cluster_label=doc.get("cluster_label"),
        risk_flags=doc.get("risk_flags"),
        target_role=doc.get("target_role"),
        timeline=doc.get("timeline"),
    )


def _merge_session_context(stored: SessionContext | None, incoming: SessionContext | None) -> SessionContext | None:
    if not stored and not incoming:
        return None
    if not stored:
        return incoming
    if not incoming:
        return stored

    return SessionContext(
        predicted_score=incoming.predicted_score if incoming.predicted_score is not None else stored.predicted_score,
        grade=incoming.grade if incoming.grade is not None else stored.grade,
        cluster_label=incoming.cluster_label if incoming.cluster_label is not None else stored.cluster_label,
        risk_flags=incoming.risk_flags if incoming.risk_flags is not None else stored.risk_flags,
        target_role=incoming.target_role if incoming.target_role is not None else stored.target_role,
        timeline=incoming.timeline if incoming.timeline is not None else stored.timeline,
    )


async def _apply_coach_tool_effects(db, user_id, effects: dict) -> None:
    if not effects:
        return
    now = datetime.now(timezone.utc)
    if "predict_refresh" in effects:
        pr = effects["predict_refresh"]
        req = PredictRequest.model_validate(pr["request"])
        resp = PredictResponse.model_validate(pr["response"])
        await db["coach_contexts"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "predicted_score": resp.score,
                    "grade": resp.grade,
                    "cluster_label": resp.cluster_label,
                    "risk_flags": [r.label for r in resp.risks],
                    "last_predict_inputs": req.model_dump(),
                    "updated_at": now,
                }
            },
            upsert=True,
        )
    if "roadmap_refresh" in effects:
        rm = effects["roadmap_refresh"]
        req = RoadmapRequest.model_validate(rm["request"])
        await db["coach_contexts"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "target_role": req.dream_role,
                    "timeline": req.timeline,
                    "last_roadmap_inputs": req.model_dump(),
                    "updated_at": now,
                }
            },
            upsert=True,
        )


@router.post("/coach", response_model=CoachResponse)
async def coach_endpoint(
    req: CoachRequest,
    request: Request,
    user: dict | None = Depends(get_optional_current_user),
) -> CoachResponse:
    db = request.app.state.db

    stored_ctx: SessionContext | None = None
    stored_messages: list[dict] = []
    last_predict_inputs: dict | None = None
    last_roadmap_inputs: dict | None = None

    if user is not None and db is not None:
        stored_ctx_doc = await db["coach_contexts"].find_one({"user_id": user["_id"]})
        stored_ctx = _doc_to_session_context(stored_ctx_doc)
        if stored_ctx_doc:
            last_predict_inputs = stored_ctx_doc.get("last_predict_inputs")
            last_roadmap_inputs = stored_ctx_doc.get("last_roadmap_inputs")

        # Load last 20 messages in chronological order
        cursor = (
            db["coach_messages"]
            .find({"user_id": user["_id"]})
            .sort("created_at", -1)
            .limit(20)
        )
        recent = await cursor.to_list(length=20)
        recent_sorted = list(reversed(recent))
        stored_messages = [
            {"role": m.get("role"), "content": m.get("content")}
            for m in recent_sorted
            if m.get("role") in {"user", "assistant"} and isinstance(m.get("content"), str)
        ]

    merged_ctx = _merge_session_context(stored_ctx, req.session_context)
    system_prompt = build_coach_agent_system_prompt(req.topic, merged_ctx, req.resume_text)

    # If authenticated, prefer DB history; otherwise fall back to request history.
    if user is not None and stored_messages:
        messages = list(stored_messages)
    else:
        trimmed_history = req.history[-20:] if req.history else []
        messages = [{"role": item.role, "content": item.content} for item in trimmed_history]

    messages.append({"role": "user", "content": req.message})

    try:
        reply, effects = await asyncio.to_thread(
            run_coach_agent_sync,
            system_prompt=system_prompt,
            messages=messages,
            last_predict_inputs=last_predict_inputs,
            last_roadmap_inputs=last_roadmap_inputs,
            resume_text_default=req.resume_text,
        )

        if user is not None and db is not None:
            await _apply_coach_tool_effects(db, user["_id"], effects)

        # Persist chat messages when authenticated
        if user is not None and db is not None:
            now = datetime.now(timezone.utc)
            await db["coach_messages"].insert_many(
                [
                    {"user_id": user["_id"], "role": "user", "content": req.message, "created_at": now},
                    {"user_id": user["_id"], "role": "assistant", "content": reply, "created_at": now},
                ]
            )
        return CoachResponse(reply=reply)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coach failed: {e}")


@router.get("/session/context", response_model=SessionContext)
async def session_context_endpoint(
    request: Request,
    user: dict | None = Depends(get_optional_current_user),
) -> SessionContext:
    db = request.app.state.db
    if user is None or db is None:
        # When not authenticated, return an empty context.
        return SessionContext()

    doc = await db["coach_contexts"].find_one({"user_id": user["_id"]})
    ctx = _doc_to_session_context(doc)
    return ctx or SessionContext()

