from __future__ import annotations

import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from pydantic import ValidationError

from models.schemas import (
    PredictToolOverrides,
    PredictResponse,
    RetrievalToolInput,
    ResumeEvalToolInput,
    RoadmapToolOverrides,
)
from services.coach_merge import merge_predict_inputs, merge_roadmap_inputs
from services.ml_engine import predict
from services.rag_service import format_retrieval_context, retrieve_guidance_context
from services.resume_eval_service import evaluate_resume_structured, format_resume_evaluation
from services.roadmap_service import generate_roadmap

COACH_AGENT_MODEL = os.getenv("GROQ_COACH_AGENT_MODEL") or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _summarize_predict(r: PredictResponse) -> str:
    risk_bits = ", ".join(f"{x.label} ({x.level})" for x in r.risks[:5])
    factor_bits = ", ".join(f"{f.label}: {f.value:.1f}" for f in r.factors[:5])
    return (
        f"Predicted score: {r.score:.1f}/100 — grade {r.grade} ({r.grade_label}). "
        f"Peer cluster: {r.cluster_label}. {r.cluster_description} "
        f"Risks: {risk_bits}. Key factors: {factor_bits}."
    )


def _summarize_roadmap_text(summary: str, n_gaps: int, n_milestones: int) -> str:
    head = summary.strip()[:800]
    return f"Roadmap generated ({n_gaps} skill gaps, {n_milestones} milestones). Summary:\n{head}"


def _make_tools(
    *,
    last_predict_inputs: dict[str, Any] | None,
    last_roadmap_inputs: dict[str, Any] | None,
    resume_text_default: str | None,
    effects: dict[str, Any],
) -> list[StructuredTool]:
    def run_academic_prediction(**kwargs: Any) -> str:
        try:
            overrides = PredictToolOverrides.model_validate(kwargs)
        except ValidationError as e:
            return f"Invalid arguments for run_academic_prediction: {e}"
        req, err = merge_predict_inputs(last_predict_inputs, overrides)
        if err or req is None:
            return err or "Missing prediction inputs."
        try:
            result = predict(req)
        except Exception as e:
            return f"Prediction failed: {e}"
        effects["predict_refresh"] = {
            "request": req.model_dump(),
            "response": result.model_dump(),
        }
        return _summarize_predict(result)

    def generate_career_roadmap(**kwargs: Any) -> str:
        try:
            overrides = RoadmapToolOverrides.model_validate(kwargs)
        except ValidationError as e:
            return f"Invalid arguments for generate_career_roadmap: {e}"
        req, err = merge_roadmap_inputs(last_roadmap_inputs, overrides)
        if err or req is None:
            return err or "Missing roadmap inputs."
        try:
            result = generate_roadmap(req)
        except Exception as e:
            return f"Roadmap generation failed: {e}"
        effects["roadmap_refresh"] = {"request": req.model_dump()}
        return _summarize_roadmap_text(
            result.summary,
            len(result.skill_gaps),
            len(result.timeline),
        )

    def evaluate_resume(**kwargs: Any) -> str:
        try:
            args = ResumeEvalToolInput.model_validate(kwargs)
        except ValidationError as e:
            return f"Invalid arguments for evaluate_resume: {e}"
        text = (args.resume_text or "").strip() or (resume_text_default or "").strip()
        if not text:
            return (
                "No resume text available. Ask the student to paste their resume in the coach resume "
                "attachment, or pass resume_text in the tool call."
            )
        if len(text) > 12000:
            text = text[:12000]
        try:
            ev = evaluate_resume_structured(
                text,
                target_role=args.target_role,
                field=args.field,
            )
        except Exception as e:
            return f"Resume evaluation failed: {e}"
        return format_resume_evaluation(ev)

    def retrieve_guidance_context_tool(**kwargs: Any) -> str:
        try:
            args = RetrievalToolInput.model_validate(kwargs)
        except ValidationError as e:
            return f"Invalid arguments for retrieve_guidance_context: {e}"
        try:
            items = retrieve_guidance_context(
                args.query,
                role=args.role,
                topic=args.topic,
                k=args.k,
            )
        except Exception as e:
            return f"Knowledge retrieval failed: {e}"
        return format_retrieval_context(items)

    return [
        StructuredTool.from_function(
            func=run_academic_prediction,
            name="run_academic_prediction",
            description=(
                "Run the academic exam score predictor (ML). Merges optional numeric overrides with "
                "the student's saved Predict form data (if any). Use when they want a (re)prediction "
                "or what-if on study inputs."
            ),
            args_schema=PredictToolOverrides,
            infer_schema=False,
        ),
        StructuredTool.from_function(
            func=generate_career_roadmap,
            name="generate_career_roadmap",
            description=(
                "Generate a structured India-focused career roadmap. Merges optional profile overrides "
                "with saved Roadmap wizard inputs (if any). Use when they want a new or updated roadmap."
            ),
            args_schema=RoadmapToolOverrides,
            infer_schema=False,
        ),
        StructuredTool.from_function(
            func=evaluate_resume,
            name="evaluate_resume",
            description=(
                "Structured resume review (scores, strengths, gaps, prioritized fixes). "
                "Uses resume_text from the tool call, or the session resume attachment if omitted."
            ),
            args_schema=ResumeEvalToolInput,
            infer_schema=False,
        ),
        StructuredTool.from_function(
            func=retrieve_guidance_context_tool,
            name="retrieve_guidance_context",
            description=(
                "Retrieve relevant guidance from the Chroma knowledge base for interview prep, career "
                "planning, skills, and resume advice. Use for factual recommendations and cite retrieved "
                "sources in the final response."
            ),
            args_schema=RetrievalToolInput,
            infer_schema=False,
        ),
    ]


def _dict_messages_to_lc(messages: list[dict[str, str]]) -> list[HumanMessage | AIMessage]:
    out: list[HumanMessage | AIMessage] = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if not isinstance(content, str):
            continue
        if role == "user":
            out.append(HumanMessage(content=content))
        elif role == "assistant":
            out.append(AIMessage(content=content))
    return out


def _extract_final_reply(messages: list[Any]) -> str:
    for m in reversed(messages):
        if not isinstance(m, AIMessage):
            continue
        tc = getattr(m, "tool_calls", None) or []
        if tc:
            continue
        c = m.content
        if isinstance(c, str) and c.strip():
            return c.strip()
        if isinstance(c, list):
            parts: list[str] = []
            for block in c:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif isinstance(block, str):
                    parts.append(block)
            joined = "".join(parts).strip()
            if joined:
                return joined
    return ""


def run_coach_agent_sync(
    *,
    system_prompt: str,
    messages: list[dict[str, str]],
    last_predict_inputs: dict[str, Any] | None,
    last_roadmap_inputs: dict[str, Any] | None,
    resume_text_default: str | None,
) -> tuple[str, dict[str, Any]]:
    """
    Run the LangGraph ReAct coach agent. Returns (assistant_reply, side_effects).

    side_effects may contain:
      - predict_refresh: {request, response} dicts from Predict models
      - roadmap_refresh: {request} from RoadmapRequest.model_dump()
    """
    effects: dict[str, Any] = {}
    tools = _make_tools(
        last_predict_inputs=last_predict_inputs,
        last_roadmap_inputs=last_roadmap_inputs,
        resume_text_default=resume_text_default,
        effects=effects,
    )
    llm = ChatGroq(
        model=COACH_AGENT_MODEL,
        temperature=0.2,
        max_tokens=1024,
    )
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
    )
    lc_messages = _dict_messages_to_lc(messages)
    result = agent.invoke(
        {"messages": lc_messages},
        config={"recursion_limit": 25},
    )
    final_messages = result.get("messages", [])
    reply = _extract_final_reply(final_messages)
    if not reply:
        reply = "I wasn't able to complete that just now. Please try rephrasing or try again in a moment."
    return reply, effects
