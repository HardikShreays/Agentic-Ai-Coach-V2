from __future__ import annotations

import json
import os
import re

from models.schemas import RoadmapRequest, RoadmapResponse
from services.groq_service import call_groq_user_prompt
from services.prompt_builder import build_roadmap_prompt

GROQ_MODEL = os.getenv("GROQ_ROADMAP_MODEL", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))


def extract_json_object(text: str) -> dict:
    if not text:
        raise ValueError("Empty response from Groq")

    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("Could not find JSON object in Groq response")
    return json.loads(match.group(0))


def generate_roadmap(req: RoadmapRequest) -> RoadmapResponse:
    prompt = build_roadmap_prompt(req)
    raw = call_groq_user_prompt(
        model=GROQ_MODEL,
        prompt=prompt,
        max_tokens=1500,
        temperature=0.2,
    )
    payload = extract_json_object(raw)
    return RoadmapResponse.model_validate(payload)
