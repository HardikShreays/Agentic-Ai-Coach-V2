from services.roadmap_service import extract_json_object


def test_extract_json_object_plain():
    d = extract_json_object('{"a": 1, "b": "x"}')
    assert d == {"a": 1, "b": "x"}


def test_extract_json_object_fenced():
    raw = """Here is JSON:
{"summary": "hi", "skill_gaps": [], "timeline": [], "courses": [], "internships": [], "resume_tips": []}
"""
    d = extract_json_object(raw)
    assert d["summary"] == "hi"
