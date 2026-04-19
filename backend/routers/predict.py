from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from models.schemas import PredictRequest, PredictResponse
from services.ml_engine import predict
from security.deps import get_optional_current_user


router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_endpoint(
    req: PredictRequest,
    request: Request,
    user: dict | None = Depends(get_optional_current_user),
) -> PredictResponse:
    try:
        result = predict(req)

        if user is not None:
            db = request.app.state.db
            if db is not None:
                await db["coach_contexts"].update_one(
                    {"user_id": user["_id"]},
                    {
                        "$set": {
                            "predicted_score": result.score,
                            "grade": result.grade,
                            "cluster_label": result.cluster_label,
                            "risk_flags": [r.label for r in result.risks],
                            "last_predict_inputs": req.model_dump(),
                            "updated_at": datetime.now(timezone.utc),
                        }
                    },
                    upsert=True,
                )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

