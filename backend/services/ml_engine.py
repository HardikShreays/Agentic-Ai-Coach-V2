from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Optional

import numpy as np

from models.schemas import (
    PredictRequest,
    PredictResponse,
    FactorItem,
    RiskItem,
)


_ML_BUNDLE: Optional[dict[str, Any]] = None

MODELS_DIR = Path(__file__).resolve().parent.parent / "models" / "ml_models"
LINEAR_MODEL_PATH = MODELS_DIR / "linear_regression.pkl"
KMEANS_BUNDLE_PATH = MODELS_DIR / "kmeans.pkl"


def _compute_engineered_features(req: PredictRequest) -> dict[str, float]:
    # Feature engineering spec (exact formulas)
    study_effort = req.hours_studied * (req.attendance / 100)
    attendance_score = req.attendance / 100
    support_system = (req.parental_involvement + req.access_to_resources + req.motivation_level) / 3
    optimal_sleep = 1 if 6 <= req.sleep_hours <= 9 else 0
    high_intensity = 1 if req.hours_studied > 30 else 0
    risk_factor = int(req.attendance < 75) + int(req.hours_studied < 10) + int(req.motivation_level == 1)

    return {
        "study_effort": float(study_effort),
        "attendance_score": float(attendance_score),
        "support_system": float(support_system),
        "optimal_sleep": float(optimal_sleep),
        "high_intensity": float(high_intensity),
        "risk_factor": float(risk_factor),
    }


def _feature_vector(req: PredictRequest) -> np.ndarray:
    feats = _compute_engineered_features(req)
    # Order matters: must match train_models.py
    return np.array(
        [
            feats["study_effort"],
            feats["attendance_score"],
            feats["support_system"],
            feats["optimal_sleep"],
            feats["high_intensity"],
            feats["risk_factor"],
        ],
        dtype=float,
    ).reshape(1, -1)


def _fallback_score(req: PredictRequest) -> float:
    feats = _compute_engineered_features(req)
    study_effort = feats["study_effort"]
    attendance_score = feats["attendance_score"]
    support_system = feats["support_system"]
    optimal_sleep = int(feats["optimal_sleep"])
    tutoring_sessions = req.tutoring_sessions
    internet_access = req.internet_access
    previous_scores = req.previous_scores
    risk_factor = int(feats["risk_factor"])

    score = (
        40
        + (study_effort * 0.38)
        + (previous_scores * 0.35)
        + (attendance_score * 8)
        + (support_system * 3.2)
        + (optimal_sleep * 2.1)
        + (tutoring_sessions * 0.9)
        + (internet_access * 1.4)
        - (risk_factor * 3.5)
    )
    score = max(40, min(100, score))
    return float(score)


def _grade_from_score(score: float) -> tuple[str, str]:
    # Grade bands (used by frontend badge colours)
    if score >= 97:
        return "A+", "Excellent Performance"
    if score >= 93:
        return "A", "Outstanding Performance"
    if score >= 85:
        return "B", "Strong Performance"
    if score >= 70:
        return "C", "Good Performance"
    return "D", "Needs Improvement"


def _compute_factors(req: PredictRequest) -> list[FactorItem]:
    feats = _compute_engineered_features(req)
    study_effort = feats["study_effort"]
    optimal_sleep = int(feats["optimal_sleep"])
    support_system = feats["support_system"]

    factors = [
        {"label": "Study Hours", "value": min(100, req.hours_studied * 2.3)},
        {"label": "Attendance", "value": req.attendance - 60},
        {"label": "Prev Score", "value": req.previous_scores - 50},
        {"label": "Sleep", "value": 85 if optimal_sleep else 38},
        {"label": "Tutoring", "value": min(100, req.tutoring_sessions * 12.5)},
        {"label": "Motivation", "value": 90 if req.motivation_level == 3 else 54 if req.motivation_level == 2 else 18},
        {"label": "Support", "value": min(100, support_system * 33)},
    ]

    # Clamp into 0..100 to keep visuals stable
    out: list[FactorItem] = []
    for f in factors:
        val = max(0.0, min(100.0, float(f["value"])))
        out.append(FactorItem(label=f["label"], value=val))
    return out


def _compute_risks(req: PredictRequest) -> list[RiskItem]:
    risks: list[RiskItem] = []
    if req.attendance < 75:
        risks.append(RiskItem(label="LOW ATTENDANCE", level="high"))
    if req.hours_studied < 10:
        risks.append(RiskItem(label="INSUFFICIENT STUDY", level="high"))
    if req.motivation_level == 1:
        risks.append(RiskItem(label="LOW MOTIVATION", level="medium"))
    if req.sleep_hours < 6 or req.sleep_hours > 9:
        risks.append(RiskItem(label="POOR SLEEP", level="medium"))
    if req.access_to_resources == 1:
        risks.append(RiskItem(label="LIMITED RESOURCES", level="medium"))
    if not risks:
        risks.append(RiskItem(label="LOW RISK PROFILE", level="low"))
    return risks


def _fallback_cluster(req: PredictRequest) -> int:
    feats = _compute_engineered_features(req)
    study_effort = feats["study_effort"]
    effort_score = study_effort + req.previous_scores * 0.5 + req.motivation_level * 5
    return 2 if effort_score > 120 else (1 if effort_score > 65 else 0)


def _cluster_label_and_description(cluster: int) -> tuple[str, str]:
    cluster_labels = {
        0: ("At-Risk Learner", "Bottom 25% — needs focused intervention."),
        1: ("Average Achiever", "Middle 50% — solid growth potential."),
        2: ("High Performer", "Top 25% of peers — keep pushing!"),
    }
    return cluster_labels[cluster]


def init_models() -> None:
    """
    Loads trained artifacts into memory.
    If artifacts are missing, prediction falls back to deterministic formulas.
    """

    global _ML_BUNDLE

    if not LINEAR_MODEL_PATH.exists() or not KMEANS_BUNDLE_PATH.exists():
        # Auto-train for a smooth "run backend and it works" experience.
        try:
            from train_models import main as train_main

            train_main()
        except Exception:
            _ML_BUNDLE = None
            return

    try:
        with open(LINEAR_MODEL_PATH, "rb") as f:
            linear_model = pickle.load(f)
        with open(KMEANS_BUNDLE_PATH, "rb") as f:
            kmeans_bundle = pickle.load(f)

        _ML_BUNDLE = {"linear_model": linear_model, "kmeans_bundle": kmeans_bundle}
    except Exception:
        _ML_BUNDLE = None


def predict(req: PredictRequest) -> PredictResponse:
    feats = _compute_engineered_features(req)
    factors = _compute_factors(req)
    risks = _compute_risks(req)
    cluster_fb = _fallback_cluster(req)
    cluster_label, cluster_description = _cluster_label_and_description(cluster_fb)

    X = _feature_vector(req)

    score: float
    cluster: int

    if _ML_BUNDLE is not None:
        try:
            lr = _ML_BUNDLE["linear_model"]
            score_pred = float(lr.predict(X)[0])
            score = max(40.0, min(100.0, score_pred))

            kmeans_bundle = _ML_BUNDLE["kmeans_bundle"]
            kmeans = kmeans_bundle["model"]
            mapping = kmeans_bundle["cluster_mapping"]  # kmeans_label -> desired_label
            raw_cluster = int(kmeans.predict(X)[0])
            cluster = int(mapping.get(raw_cluster, cluster_fb))
            cluster_label, cluster_description = _cluster_label_and_description(cluster)
        except Exception:
            score = _fallback_score(req)
            cluster = cluster_fb
            cluster_label, cluster_description = _cluster_label_and_description(cluster)
    else:
        score = _fallback_score(req)
        cluster = cluster_fb
        cluster_label, cluster_description = _cluster_label_and_description(cluster)

    grade, grade_label = _grade_from_score(score)

    return PredictResponse(
        score=float(score),
        grade=grade,
        grade_label=grade_label,
        factors=factors,
        risks=risks,
        cluster=cluster,
        cluster_label=cluster_label,
        cluster_description=cluster_description,
    )

