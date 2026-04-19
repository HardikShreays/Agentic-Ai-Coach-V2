from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FactorItem(BaseModel):
    label: str
    value: float


class RiskItem(BaseModel):
    label: str
    level: str  # high | medium | low


class PredictRequest(BaseModel):
    hours_studied: float  # 0–44
    attendance: float  # 60–100
    previous_scores: float  # 50–100
    sleep_hours: float  # 4–10
    tutoring_sessions: float  # 0–8
    parental_involvement: int  # 1–3
    access_to_resources: int  # 1–3
    motivation_level: int  # 1–3
    internet_access: int  # 0 or 1


class PredictResponse(BaseModel):
    score: float
    grade: str  # A+, A, B, C, D
    grade_label: str
    factors: list[FactorItem]
    risks: list[RiskItem]
    cluster: int  # 0, 1, 2
    cluster_label: str
    cluster_description: str


class SkillGap(BaseModel):
    skill: str
    current: int = Field(ge=0, le=100)
    required: int = Field(ge=0, le=100)
    priority: str  # High | Medium | Low


class TimelineItem(BaseModel):
    month: str
    title: str
    description: str
    emoji: str


class Course(BaseModel):
    name: str
    platform: str
    duration: str
    type: str  # Free | Paid


class Internship(BaseModel):
    title: str
    platform: str
    emoji: str
    tips: str


class RoadmapRequest(BaseModel):
    name: str
    stage: str
    field: str
    score: Optional[str] = None
    skills: list[str]
    dream_role: str
    timeline: str
    weekly_hours: str
    context: Optional[str] = None


class RoadmapResponse(BaseModel):
    summary: str
    skill_gaps: list[SkillGap]
    timeline: list[TimelineItem]
    courses: list[Course]
    internships: list[Internship]
    resume_tips: list[str]


class SessionContext(BaseModel):
    predicted_score: Optional[float] = None
    grade: Optional[str] = None
    cluster_label: Optional[str] = None
    risk_flags: Optional[list[str]] = None
    target_role: Optional[str] = None
    timeline: Optional[str] = None


class ChatHistoryItem(BaseModel):
    role: str  # user | assistant
    content: str


class CoachRequest(BaseModel):
    message: str
    history: list[ChatHistoryItem]
    topic: str  # career|skills|interview|resume|motivation
    session_context: Optional[SessionContext] = None
    resume_text: Optional[str] = Field(default=None, max_length=12000)


class CoachResponse(BaseModel):
    reply: str


# --- Resume evaluation (structured LLM output) ---


class ResumeEvaluation(BaseModel):
    """Structured resume feedback for India placement / ATS-style review."""

    one_line_verdict: str
    overall_score: int = Field(ge=0, le=100)
    format_score: int = Field(ge=0, le=100)
    content_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    prioritized_fixes: list[str] = Field(default_factory=list)


# --- Optional tool override payloads (all fields optional for LLM tool args) ---


class PredictToolOverrides(BaseModel):
    hours_studied: Optional[float] = None
    attendance: Optional[float] = None
    previous_scores: Optional[float] = None
    sleep_hours: Optional[float] = None
    tutoring_sessions: Optional[float] = None
    parental_involvement: Optional[int] = None
    access_to_resources: Optional[int] = None
    motivation_level: Optional[int] = None
    internet_access: Optional[int] = None


class RoadmapToolOverrides(BaseModel):
    name: Optional[str] = None
    stage: Optional[str] = None
    field: Optional[str] = None
    score: Optional[str] = None
    skills: Optional[list[str]] = None
    dream_role: Optional[str] = None
    timeline: Optional[str] = None
    weekly_hours: Optional[str] = None
    context: Optional[str] = None


class ResumeEvalToolInput(BaseModel):
    resume_text: Optional[str] = Field(default=None, max_length=12000)
    target_role: Optional[str] = None
    field: Optional[str] = None


class RetrievalToolInput(BaseModel):
    query: str
    role: Optional[str] = None
    topic: Optional[str] = None
    k: int = Field(default=4, ge=1, le=8)

