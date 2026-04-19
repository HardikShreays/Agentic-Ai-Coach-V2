from __future__ import annotations

import os

from models.schemas import ResumeEvaluation
from services.groq_service import call_groq_user_prompt
from services.roadmap_service import extract_json_object

GROQ_MODEL = os.getenv("GROQ_RESUME_EVAL_MODEL", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))


def build_resume_eval_prompt(
    resume_text: str,
    *,
    target_role: str | None,
    field: str | None,
) -> str:
    role_line = target_role or "Not specified"
    field_line = field or "Not specified"
    return f"""You are an expert resume reviewer for Indian campus placements and early-career hiring.
Evaluate the resume below for clarity, impact, formatting for ATS, and alignment with the student's stated direction.

Target role (if any): {role_line}
Field / branch (if any): {field_line}

RESUME TEXT:
---
{resume_text}
---

Return ONLY raw JSON (no markdown, no code fences) with this exact shape:
{{
  "one_line_verdict": "One sentence summary",
  "overall_score": 0-100,
  "format_score": 0-100,
  "content_score": 0-100,
  "strengths": ["3-5 concrete strengths"],
  "gaps": ["3-5 specific gaps or risks"],
  "prioritized_fixes": ["3-5 ordered fixes — most important first"]
}}

Be honest and specific. Reference India-relevant norms (CGPA, projects, DSA, internships) only when applicable to what is written."""


def evaluate_resume_structured(
    resume_text: str,
    *,
    target_role: str | None = None,
    field: str | None = None,
) -> ResumeEvaluation:
    prompt = build_resume_eval_prompt(resume_text, target_role=target_role, field=field)
    raw = call_groq_user_prompt(
        model=GROQ_MODEL,
        prompt=prompt,
        max_tokens=1200,
        temperature=0.2,
    )
    payload = extract_json_object(raw)
    return ResumeEvaluation.model_validate(payload)


def format_resume_evaluation(ev: ResumeEvaluation) -> str:
    lines = [
        f"Verdict: {ev.one_line_verdict}",
        f"Scores — overall: {ev.overall_score}/100, format: {ev.format_score}/100, content: {ev.content_score}/100",
        "",
        "### Strengths",
        *[f"- {s}" for s in ev.strengths],
        "",
        "### Gaps",
        *[f"- {g}" for g in ev.gaps],
        "",
        "### Prioritized fixes",
        *[f"{i + 1}. {f}" for i, f in enumerate(ev.prioritized_fixes)],
    ]
    return "\n".join(lines)
