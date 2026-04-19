from models.schemas import PredictToolOverrides, RoadmapToolOverrides
from services.coach_merge import merge_predict_inputs, merge_roadmap_inputs


def test_merge_predict_saved_plus_override():
    saved = {
        "hours_studied": 20.0,
        "attendance": 80.0,
        "previous_scores": 70.0,
        "sleep_hours": 7.0,
        "tutoring_sessions": 1.0,
        "parental_involvement": 2,
        "access_to_resources": 2,
        "motivation_level": 2,
        "internet_access": 1,
    }
    req, err = merge_predict_inputs(saved, PredictToolOverrides(attendance=95.0))
    assert err is None
    assert req is not None
    assert req.attendance == 95.0
    assert req.hours_studied == 20.0


def test_merge_predict_missing_returns_error():
    req, err = merge_predict_inputs(None, PredictToolOverrides())
    assert req is None
    assert err is not None


def test_merge_roadmap_saved_plus_override():
    saved = {
        "name": "A",
        "stage": "UG2",
        "field": "CS",
        "skills": ["Python"],
        "dream_role": "SDE",
        "timeline": "6 months",
        "weekly_hours": "10",
    }
    req, err = merge_roadmap_inputs(saved, RoadmapToolOverrides(dream_role="ML Engineer"))
    assert err is None
    assert req is not None
    assert req.dream_role == "ML Engineer"
    assert req.name == "A"


def test_merge_roadmap_empty_returns_error():
    req, err = merge_roadmap_inputs(None, RoadmapToolOverrides())
    assert req is None
    assert err is not None
