from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from models.schemas import (
    PredictRequest,
    PredictToolOverrides,
    RoadmapRequest,
    RoadmapToolOverrides,
)


def merge_predict_inputs(
    saved: dict[str, Any] | None,
    overrides: PredictToolOverrides,
) -> tuple[PredictRequest | None, str | None]:
    patch = overrides.model_dump(exclude_none=True)
    merged = {**(saved or {}), **patch}
    if not merged:
        return None, (
            "No prediction inputs available. Ask the student for their study habits and scores "
            "(hours studied, attendance, previous scores, sleep, tutoring, parental involvement, "
            "resources, motivation, internet access), or have them run Predict first."
        )
    try:
        return PredictRequest.model_validate(merged), None
    except ValidationError as e:
        return None, f"Invalid or incomplete prediction inputs after merge: {e}"


def merge_roadmap_inputs(
    saved: dict[str, Any] | None,
    overrides: RoadmapToolOverrides,
) -> tuple[RoadmapRequest | None, str | None]:
    patch = overrides.model_dump(exclude_none=True)
    merged = {**(saved or {}), **patch}
    if not merged:
        return None, (
            "No roadmap profile available. Ask for name, stage, field, skills, dream role, "
            "timeline, weekly hours—or have the student generate a roadmap first."
        )
    try:
        return RoadmapRequest.model_validate(merged), None
    except ValidationError as e:
        return None, f"Invalid or incomplete roadmap inputs after merge: {e}"
