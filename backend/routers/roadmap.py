from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from models.schemas import RoadmapRequest, RoadmapResponse
from services.roadmap_service import generate_roadmap
from security.deps import get_optional_current_user


router = APIRouter()


@router.post("/roadmap", response_model=RoadmapResponse)
async def roadmap_endpoint(
    req: RoadmapRequest,
    request: Request,
    user: dict | None = Depends(get_optional_current_user),
) -> RoadmapResponse:
    try:
        result = generate_roadmap(req)

        if user is not None:
            db = request.app.state.db
            if db is not None:
                await db["coach_contexts"].update_one(
                    {"user_id": user["_id"]},
                    {
                        "$set": {
                            "target_role": req.dream_role,
                            "timeline": req.timeline,
                            "last_roadmap_inputs": req.model_dump(),
                            "updated_at": datetime.now(timezone.utc),
                        }
                    },
                    upsert=True,
                )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {e}")

