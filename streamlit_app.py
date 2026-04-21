from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

# Silence Chroma telemetry errors in some local environments.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import streamlit as st
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from urllib import error, request

try:
    import chromadb  # type: ignore
except Exception:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
    SentenceTransformer = None

st.set_page_config(page_title="AcadPipeline", page_icon="🎓", layout="wide")

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
KB_FILE = DATA_DIR / "knowledge_base.json"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
VECTOR_COLLECTION = "acadpipeline_kb"
ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env_file() -> None:
    if not ENV_FILE.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(ENV_FILE)
        return
    except Exception:
        pass

    # Fallback parser for setups without python-dotenv.
    try:
        for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        return


_load_env_file()


def _get_groq_api_key() -> str:
    env_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if env_key:
        return env_key
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
        if isinstance(secret_key, str):
            return secret_key.strip()
    except Exception:
        pass
    return ""


def _grade(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text)]


def _jaccard_score(query: str, doc: str) -> float:
    q = set(_tokenize(query))
    d = set(_tokenize(doc))
    if not q or not d:
        return 0.0
    return len(q & d) / len(q | d)


def _default_kb_docs() -> list[dict[str, str]]:
    return [
        {
            "title": "DSA Preparation",
            "content": "Practice arrays, strings, dynamic programming, trees and graphs. Solve problems consistently and review patterns.",
        },
        {
            "title": "Resume Improvement",
            "content": "Use action verbs, measurable impact, concise bullet points and role-aligned project summaries.",
        },
        {
            "title": "Interview Readiness",
            "content": "Prepare behavioral stories with STAR framework, revise core CS fundamentals and mock interviews weekly.",
        },
        {
            "title": "Roadmap Strategy",
            "content": "Split goals into monthly milestones, pick one primary stack, and ship portfolio projects with documentation.",
        },
    ]


def _load_kb() -> list[dict[str, str]]:
    if not KB_FILE.exists():
        return []
    try:
        data = json.loads(KB_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict) and "title" in d and "content" in d]
        return []
    except Exception:
        return []


@st.cache_resource
def _get_embedding_model():
    if SentenceTransformer is None:
        return None
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def _vector_db_available() -> bool:
    return chromadb is not None and _get_embedding_model() is not None


def _embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_embedding_model()
    if model is None:
        return []
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def _rebuild_vector_index_from_kb() -> bool:
    docs = _load_kb()
    if not docs or not _vector_db_available():
        return False
    try:
        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        collection = client.get_or_create_collection(name=VECTOR_COLLECTION, metadata={"hnsw:space": "cosine"})
        existing = collection.get()
        existing_ids = existing.get("ids", []) if isinstance(existing, dict) else []
        if existing_ids:
            collection.delete(ids=existing_ids)

        doc_texts = [d["content"] for d in docs]
        doc_ids = [f"doc-{idx}" for idx in range(len(docs))]
        metadatas = [{"title": d["title"]} for d in docs]
        embeddings = _embed_texts(doc_texts)
        if not embeddings:
            return False
        collection.add(ids=doc_ids, documents=doc_texts, metadatas=metadatas, embeddings=embeddings)
        return True
    except Exception:
        return False


def _ingest_kb(raw_text: str) -> int:
    blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
    docs: list[dict[str, str]] = []
    for i, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        title = lines[0][:80].strip() or f"Document {i}"
        docs.append({"title": title, "content": block})
    KB_FILE.write_text(json.dumps(docs, indent=2), encoding="utf-8")
    _rebuild_vector_index_from_kb()
    return len(docs)


def _retrieve_context(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    if _vector_db_available():
        try:
            client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
            collection = client.get_or_create_collection(name=VECTOR_COLLECTION, metadata={"hnsw:space": "cosine"})
            # Lazy (re)build when collection is empty or missing docs.
            peek = collection.peek(limit=1)
            if not peek.get("ids"):
                _rebuild_vector_index_from_kb()
                collection = client.get_or_create_collection(name=VECTOR_COLLECTION, metadata={"hnsw:space": "cosine"})

            query_embedding = _embed_texts([query])
            if query_embedding:
                res = collection.query(
                    query_embeddings=query_embedding,
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"],
                )
                docs_out = res.get("documents", [[]])
                metas_out = res.get("metadatas", [[]])
                dists_out = res.get("distances", [[]])
                hits: list[dict[str, Any]] = []
                if docs_out and metas_out and dists_out:
                    for doc_text, meta, dist in zip(docs_out[0], metas_out[0], dists_out[0]):
                        title = meta.get("title", "Knowledge Doc") if isinstance(meta, dict) else "Knowledge Doc"
                        score = max(0.0, min(1.0, 1.0 - float(dist)))
                        hits.append({"doc": {"title": title, "content": doc_text}, "score": score})
                if hits:
                    return hits
        except Exception:
            pass

    # Fallback lexical retrieval when vector-db path is unavailable.
    docs = _load_kb()
    ranked = sorted(
        [{"doc": d, "score": _jaccard_score(query, d["content"])} for d in docs],
        key=lambda x: x["score"],
        reverse=True,
    )
    return [r for r in ranked[:top_k] if r["score"] > 0.0]


def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    cleaned = text.strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _heuristic_plan_from_prompt(user_prompt: str) -> dict[str, Any]:
    prompt = user_prompt.lower()
    timeline_match = re.search(r"\b(3|6|12)[-\s]?month", prompt)
    timeline = f"{timeline_match.group(1)} months" if timeline_match else "6 months"
    role_match = re.search(r"for\s+([a-zA-Z][a-zA-Z0-9\s/&-]{2,40})", user_prompt, flags=re.IGNORECASE)
    role = role_match.group(1).strip(" .,!?:;") if role_match else "Software Engineer"

    if "roadmap" in prompt or "plan" in prompt:
        return {
            "action": "tool",
            "tool_name": "generate_roadmap",
            "args": {
                "role": role,
                "timeline": timeline if timeline in {"3 months", "6 months", "12 months"} else "6 months",
                "skills": [],
                "weekly_hours": 10,
                "context": "",
            },
            "reason": "Detected roadmap request from user prompt.",
        }
    if "resume" in prompt and ("evaluate" in prompt or "review" in prompt or "score" in prompt):
        return {
            "action": "tool",
            "tool_name": "evaluate_resume_ai",
            "args": {"target_role": "Software Engineer"},
            "reason": "Detected resume evaluation request.",
        }
    return {"action": "respond", "tool_name": "", "args": {}, "reason": "No tool intent detected."}


class CoachRAGState(dict):
    """Typed-like state container for LangGraph coach pipeline."""


def _rag_retrieve_node(state: CoachRAGState) -> CoachRAGState:
    query = state.get("query", "")
    hits = _retrieve_context(query)
    state["context_hits"] = hits
    state["context_text"] = "\n".join(
        [f"{idx + 1}. {hit['doc']['title']}: {hit['doc']['content']}" for idx, hit in enumerate(hits)]
    )
    return state


def _agent_decide_node(state: CoachRAGState) -> CoachRAGState:
    user_prompt = state.get("query", "")
    system_prompt = (
        "You are a planner for a student coaching agent.\n"
        "Pick at most one tool to call based on user intent.\n"
        "Available tools and strict args:\n"
        "- evaluate_resume: {resume_text: str, target_role: str}\n"
        "- evaluate_resume_ai: {resume_text?: str, target_role?: str} (uses latest resume from session when omitted)\n"
        "- generate_roadmap: {role: str, timeline: '3 months'|'6 months'|'12 months', skills: [str], weekly_hours: int, context: str}\n"
        "- predict_score: {hours: float, attendance: float, previous: float, sleep: float, motivation: int}\n"
        "Return ONLY JSON with shape: "
        '{"action":"tool|respond","tool_name":"...","args":{...},"reason":"..."}.\n'
        "If required fields are missing, choose action=respond."
    )
    raw = _groq_chat(system_prompt, f"User message: {user_prompt}") or ""
    state["planner_llm_error"] = st.session_state.get("last_groq_error", "")
    plan = _extract_json_object(raw)
    if not plan:
        plan = _heuristic_plan_from_prompt(user_prompt)
    elif str(plan.get("action", "")).lower() != "tool":
        heuristic = _heuristic_plan_from_prompt(user_prompt)
        if heuristic.get("action") == "tool":
            plan = heuristic
    state["plan"] = plan
    return state


def _agent_run_tool_node(state: CoachRAGState) -> CoachRAGState:
    plan = state.get("plan", {})
    tool_name = plan.get("tool_name", "")
    args = plan.get("args", {}) if isinstance(plan.get("args"), dict) else {}
    tool_result: dict[str, Any] = {"tool_name": tool_name, "ok": False, "result": None, "error": None}
    try:
        registry = _tool_registry()
        selected_tool = registry.get(tool_name)
        if selected_tool is None:
            tool_result["error"] = "No executable tool selected."
        else:
            prepared_args = _prepare_tool_args(tool_name, args)
            if isinstance(prepared_args, dict) and prepared_args.get("__error__"):
                tool_result["error"] = prepared_args["__error__"]
            else:
                result = selected_tool.invoke(prepared_args)
                _sync_tool_result_to_session(tool_name, result)
                tool_result["result"] = result
                tool_result["ok"] = True
    except Exception as exc:
        tool_result["error"] = str(exc)
    state["tool_result"] = tool_result
    return state


def _should_run_tool(state: CoachRAGState) -> str:
    plan = state.get("plan", {})
    action = str(plan.get("action", "respond")).lower()
    tool_name = str(plan.get("tool_name", ""))
    if action == "tool" and tool_name in {"evaluate_resume", "evaluate_resume_ai", "generate_roadmap", "predict_score"}:
        return "run_tool"
    return "generate"


def _rag_generate_node(state: CoachRAGState) -> CoachRAGState:
    user_prompt = state.get("query", "")
    predict_result = st.session_state.get("predict_result")
    roadmap = st.session_state.get("roadmap")
    context_text = state.get("context_text", "")
    tool_result = state.get("tool_result")

    system_prompt = (
        "You are a concise career coach for college students. "
        "Give practical next steps and avoid generic motivation-only advice. "
        "If a tool_result exists, use it explicitly in the answer."
    )
    user_context = (
        f"User message: {user_prompt}\n"
        f"Predicted score context: {predict_result}\n"
        f"Roadmap context: {roadmap}\n"
        f"Tool result context: {tool_result}\n"
        f"Knowledge context:\n{context_text}"
    )

    llm_reply = _groq_chat(system_prompt, user_context)
    if llm_reply:
        state["llm_mode"] = "groq"
        state["reply"] = llm_reply
        return state
    state["llm_mode"] = "local_fallback"
    state["llm_error"] = st.session_state.get("last_groq_error", "")

    if tool_result and tool_result.get("ok"):
        name = tool_result.get("tool_name")
        result = tool_result.get("result")
        if name == "generate_roadmap" and isinstance(result, dict):
            milestones = result.get("milestones", [])
            top_milestones = "\n".join([
                (
                    f"- Month {m.get('month')}: {m.get('task')}\n"
                    f"  Topics: {', '.join(m.get('topics', [])[:2])}\n"
                    f"  Deliverable: {m.get('deliverable', 'Portfolio task')}"
                )
                for m in milestones[:3]
                if isinstance(m, dict)
            ])
            state["reply"] = (
                f"Generated your roadmap: {result.get('summary', '')}\n\n"
                f"Start with these milestones:\n{top_milestones or '- Month 1: Set foundation and revise core concepts.'}\n\n"
                f"Weekly measurable goal: {(result.get('measurable_goals') or ['Track weekly hours and complete 2 mocks.'])[0]}"
            )
            return state
        if name == "predict_score" and isinstance(result, dict):
            state["reply"] = (
                f"Prediction complete: {result.get('score')}/100 ({result.get('grade')}). "
                f"Cluster: {result.get('cluster')}."
            )
            return state
        if name == "evaluate_resume" and isinstance(result, dict):
            state["reply"] = (
                f"Resume evaluation complete: {result.get('overall')}/100 - {result.get('verdict')}.\n"
                f"Top gap: {(result.get('gaps') or ['No major gaps detected.'])[0]}"
            )
            return state
        if name == "evaluate_resume_ai" and isinstance(result, dict):
            state["reply"] = (
                f"AI resume evaluation complete: {result.get('overall')}/100 - {result.get('verdict')}.\n"
                f"Top strengths: {', '.join((result.get('strengths') or ['Not available'])[:2])}\n"
                f"Top gap: {(result.get('gaps') or ['No major gaps detected.'])[0]}"
            )
            return state

    state["reply"] = _local_coach_reply(
        user_prompt,
        predict_result["score"] if predict_result else None,
        roadmap,
        state.get("context_hits", []),
    )
    return state


@st.cache_resource
def _build_coach_rag_graph():
    graph = StateGraph(dict)
    graph.add_node("retrieve", _rag_retrieve_node)
    graph.add_node("decide", _agent_decide_node)
    graph.add_node("run_tool", _agent_run_tool_node)
    graph.add_node("generate", _rag_generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "decide")
    graph.add_conditional_edges("decide", _should_run_tool, {"run_tool": "run_tool", "generate": "generate"})
    graph.add_edge("run_tool", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


def _predict_score(hours: float, attendance: float, previous: float, sleep: float, motivation: int) -> dict[str, Any]:
    normalized = (
        (hours / 50.0) * 22.0
        + (attendance / 100.0) * 26.0
        + (previous / 100.0) * 30.0
        + (sleep / 10.0) * 10.0
        + (motivation / 5.0) * 12.0
    )
    score = max(0.0, min(100.0, round(normalized, 1)))
    risks: list[dict[str, str]] = []
    if attendance < 75:
        risks.append({"label": "Low attendance", "level": "high"})
    if sleep < 6:
        risks.append({"label": "Sleep debt", "level": "medium"})
    if hours < 10:
        risks.append({"label": "Low study hours", "level": "medium"})
    if motivation <= 2:
        risks.append({"label": "Motivation dip", "level": "medium"})
    if not risks:
        risks.append({"label": "No major risk flags", "level": "low"})
    cluster = "High Performer" if score >= 85 else "Progress Builder" if score >= 65 else "Needs Support"
    factors = [
        {"label": "Hours studied", "value": hours},
        {"label": "Attendance", "value": attendance},
        {"label": "Previous score", "value": previous},
        {"label": "Sleep", "value": sleep},
        {"label": "Motivation", "value": float(motivation)},
    ]
    return {"score": score, "grade": _grade(score), "cluster": cluster, "factors": factors, "risks": risks}


def _generate_roadmap(role: str, timeline: str, skills: list[str], weekly_hours: int, context: str) -> dict[str, Any]:
    months = {"3 months": 3, "6 months": 6, "12 months": 12}[timeline]
    role_key = role.lower()
    role_is_data = any(k in role_key for k in ["data analyst", "analyst", "business analyst", "bi analyst"])

    if role_is_data:
        topic_pool = [
            "Excel advanced formulas (INDEX/MATCH, XLOOKUP), PivotTables, data cleaning",
            "SQL fundamentals: SELECT, JOINs, GROUP BY, HAVING, window functions",
            "Statistics for analytics: distributions, hypothesis testing, confidence intervals",
            "Python for analysis: pandas, numpy, matplotlib/seaborn",
            "Dashboarding: Power BI or Tableau with business KPIs",
            "Case studies: conversion funnel, retention/churn, cohort and A/B analysis",
            "Storytelling: insight framing, recommendations, stakeholder communication",
        ]
        project_pool = [
            "E-commerce sales dashboard with month-over-month KPI tracking",
            "Customer churn analysis with segment-level recommendations",
            "Marketing campaign performance analysis with attribution insights",
        ]
        interview_pool = [
            "SQL query drills (easy-medium joins and aggregations)",
            "Product metrics and business case walkthroughs",
            "Explain one dashboard and one analysis end-to-end",
        ]
        certs = ["Google Data Analytics", "Microsoft PL-300 (Power BI)", "SQL HackerRank practice track"]
    else:
        topic_pool = [
            "Core DSA patterns: arrays, strings, hash maps, trees, graphs, DP",
            "Language depth in primary stack (Python/Java/JS): OOP, error handling, testing",
            "Backend fundamentals: REST APIs, auth, database modeling",
            "System design basics: scalability, caching, queues, CAP trade-offs",
            "Cloud/devops basics: Docker, CI/CD, deployment and monitoring",
            "Behavioral preparation with STAR and impact storytelling",
        ]
        project_pool = [
            "Full-stack CRUD app with auth and role-based access",
            "Scalable API service with caching and async processing",
            "Production-style deployed portfolio project with tests",
        ]
        interview_pool = [
            "2 coding rounds/week and 1 timed mock round",
            "System design whiteboard for one common architecture/week",
            "Behavioral stories for conflict, impact, leadership, failure",
        ]
        certs = ["AWS Cloud Practitioner", "Meta Backend/Frontend cert", "System Design primer track"]

    milestones = []
    for month in range(1, months + 1):
        topic_idx_start = ((month - 1) * 2) % len(topic_pool)
        month_topics = topic_pool[topic_idx_start : topic_idx_start + 2]
        if len(month_topics) < 2:
            month_topics += topic_pool[: 2 - len(month_topics)]

        if month == 1:
            task = "Foundation sprint: set baseline, close fundamentals, and build study system."
        elif month <= max(2, months // 2):
            task = "Skill build: complete core topics and create mini deliverables."
        elif month < months:
            task = "Portfolio + applied practice: ship strong project artifacts."
        else:
            task = "Interview and placement sprint: applications, mocks, and polishing."

        milestones.append(
            {
                "month": month,
                "task": task,
                "topics": month_topics,
                "deliverable": project_pool[(month - 1) % len(project_pool)],
                "interview_focus": interview_pool[(month - 1) % len(interview_pool)],
            }
        )

    weekly_plan = [
        {"day": "Mon", "focus": "Learn new topic (90-120 min) + notes"},
        {"day": "Tue", "focus": "Hands-on practice/problem set (90-120 min)"},
        {"day": "Wed", "focus": "Mini-project/dashboard/code implementation"},
        {"day": "Thu", "focus": "Revision + weak area drill"},
        {"day": "Fri", "focus": "Mock interview/case/quiz"},
        {"day": "Sat", "focus": "Portfolio polish + LinkedIn/GitHub update"},
        {"day": "Sun", "focus": "Weekly review: track KPIs, plan next week"},
    ]

    courses = [
        {"name": f"{role} Fundamentals", "platform": "Coursera / YouTube", "duration": "6-8 weeks"},
        {"name": "Practical Project Track", "platform": "Kaggle / GitHub / Personal", "duration": "8-12 weeks"},
        {"name": "Interview Preparation Track", "platform": "LeetCode / Case Library", "duration": "4-6 weeks"},
    ]

    measurable_goals = [
        f"Study {weekly_hours} focused hours every week.",
        "Publish at least 1 portfolio artifact every 4 weeks.",
        "Complete 2 interview practice sessions every week.",
    ]

    return {
        "summary": f"Detailed {timeline} plan for {role} with {weekly_hours} hours/week and concrete monthly deliverables.",
        "skills": skills,
        "context": context,
        "milestones": milestones,
        "courses": courses,
        "topic_pool": topic_pool,
        "projects": project_pool,
        "interview_prep": interview_pool,
        "certifications": certs,
        "weekly_plan": weekly_plan,
        "measurable_goals": measurable_goals,
    }


def _evaluate_resume(resume_text: str, target_role: str) -> dict[str, Any]:
    text = resume_text.lower()
    sections = {
        "education": "education" in text,
        "projects": "project" in text,
        "skills": "skill" in text,
        "experience": "experience" in text or "internship" in text,
    }
    metrics_count = len(re.findall(r"\b\d+%|\b\d+\+|\$\d+", resume_text))
    bullet_count = len(re.findall(r"^\s*[-*]", resume_text, flags=re.MULTILINE))
    section_score = sum(1 for v in sections.values() if v) * 20
    impact_score = min(20, metrics_count * 4)
    structure_score = min(20, bullet_count // 2)
    role_bonus = 10 if target_role.strip() and target_role.lower() in text else 0
    overall = min(100, section_score + impact_score + structure_score + role_bonus)
    strengths = []
    gaps = []
    if sections["projects"]:
        strengths.append("Projects section present.")
    else:
        gaps.append("Add a dedicated projects section with outcomes.")
    if metrics_count >= 2:
        strengths.append("Includes quantifiable impact.")
    else:
        gaps.append("Add metrics such as percentages, numbers, or outcomes.")
    if bullet_count >= 6:
        strengths.append("Readable bullet-based format.")
    else:
        gaps.append("Use concise bullets for each role/project.")
    if not sections["experience"]:
        gaps.append("Add internship, volunteer, or practical work experience.")
    verdict = "Strong profile" if overall >= 75 else "Good base, needs polish" if overall >= 55 else "Needs major improvements"
    return {
        "overall": overall,
        "verdict": verdict,
        "strengths": strengths or ["Clear intent and role focus."],
        "gaps": gaps or ["No major structural gaps detected."],
    }


def _evaluate_resume_ai(resume_text: str, target_role: str) -> dict[str, Any]:
    base_report = _evaluate_resume(resume_text, target_role)
    system_prompt = (
        "You are an ATS and hiring resume reviewer. "
        "Return ONLY JSON with keys: overall (0-100 int), verdict (str), strengths (list[str]), gaps (list[str]). "
        "Be specific and actionable for college students."
    )
    user_prompt = (
        f"Target role: {target_role}\n"
        f"Resume text:\n{resume_text}\n\n"
        f"Base rule-based report for calibration: {base_report}"
    )
    raw = _groq_chat(system_prompt, user_prompt)
    parsed = _extract_json_object(raw or "")
    if not parsed:
        return base_report
    try:
        overall = int(parsed.get("overall", base_report["overall"]))
    except (TypeError, ValueError):
        overall = int(base_report["overall"])
    strengths = parsed.get("strengths", base_report["strengths"])
    gaps = parsed.get("gaps", base_report["gaps"])
    if not isinstance(strengths, list) or not all(isinstance(x, str) for x in strengths):
        strengths = base_report["strengths"]
    if not isinstance(gaps, list) or not all(isinstance(x, str) for x in gaps):
        gaps = base_report["gaps"]
    verdict = parsed.get("verdict", base_report["verdict"])
    if not isinstance(verdict, str):
        verdict = base_report["verdict"]
    return {
        "overall": max(0, min(100, overall)),
        "verdict": verdict,
        "strengths": strengths[:5] if strengths else base_report["strengths"],
        "gaps": gaps[:5] if gaps else base_report["gaps"],
    }


@tool
def predict_score_tool(hours: float, attendance: float, previous: float, sleep: float, motivation: int) -> dict[str, Any]:
    """Predict performance score from study, attendance, sleep, and motivation."""
    return _predict_score(float(hours), float(attendance), float(previous), float(sleep), int(motivation))


@tool
def generate_roadmap_tool(
    role: str,
    timeline: str,
    skills: list[str] | None = None,
    weekly_hours: int = 10,
    context: str = "",
) -> dict[str, Any]:
    """Generate a role-based roadmap with milestones and measurable goals."""
    safe_role = role.strip() or "Software Engineer"
    safe_timeline = timeline if timeline in {"3 months", "6 months", "12 months"} else "6 months"
    safe_skills = [str(s).strip() for s in (skills or []) if str(s).strip()]
    safe_weekly_hours = max(3, min(30, int(weekly_hours)))
    return _generate_roadmap(safe_role, safe_timeline, safe_skills, safe_weekly_hours, str(context))


@tool
def evaluate_resume_tool(resume_text: str, target_role: str = "Software Engineer") -> dict[str, Any]:
    """Run rule-based resume evaluation and return strengths and gaps."""
    return _evaluate_resume(resume_text.strip(), target_role.strip() or "Software Engineer")


@tool
def evaluate_resume_ai_tool(resume_text: str, target_role: str = "Software Engineer") -> dict[str, Any]:
    """Run AI-powered resume evaluation with structured feedback."""
    return _evaluate_resume_ai(resume_text.strip(), target_role.strip() or "Software Engineer")


def _tool_registry():
    return {
        "predict_score": predict_score_tool,
        "generate_roadmap": generate_roadmap_tool,
        "evaluate_resume": evaluate_resume_tool,
        "evaluate_resume_ai": evaluate_resume_ai_tool,
    }


def _prepare_tool_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "evaluate_resume_ai":
        resume_text = str(args.get("resume_text", "")).strip() or st.session_state.get("latest_resume_text", "")
        target_role = (
            str(args.get("target_role", "")).strip()
            or st.session_state.get("latest_resume_target_role", "")
            or "Software Engineer"
        )
        if not resume_text:
            return {
                "__error__": "Missing resume text. Paste resume in Resume Evaluation page first, or provide it in chat."
            }
        return {"resume_text": resume_text, "target_role": target_role}

    if tool_name == "evaluate_resume":
        resume_text = str(args.get("resume_text", "")).strip()
        target_role = str(args.get("target_role", "Software Engineer")).strip() or "Software Engineer"
        if not resume_text:
            return {"__error__": "Missing required arg: resume_text."}
        return {"resume_text": resume_text, "target_role": target_role}

    if tool_name == "generate_roadmap":
        raw_skills = args.get("skills", [])
        skills = [str(s).strip() for s in raw_skills] if isinstance(raw_skills, list) else []
        return {
            "role": str(args.get("role", "Software Engineer")).strip() or "Software Engineer",
            "timeline": str(args.get("timeline", "6 months")),
            "skills": skills,
            "weekly_hours": int(args.get("weekly_hours", 10)),
            "context": str(args.get("context", "")),
        }

    if tool_name == "predict_score":
        return {
            "hours": float(args.get("hours", 16.0)),
            "attendance": float(args.get("attendance", 82.0)),
            "previous": float(args.get("previous", 75.0)),
            "sleep": float(args.get("sleep", 7.0)),
            "motivation": int(args.get("motivation", 3)),
        }

    return args


def _sync_tool_result_to_session(tool_name: str, result: Any) -> None:
    if tool_name == "generate_roadmap" and isinstance(result, dict):
        st.session_state["roadmap"] = result
    elif tool_name == "predict_score" and isinstance(result, dict):
        st.session_state["predict_result"] = result


def _groq_chat(system_prompt: str, user_prompt: str) -> str | None:
    api_key = _get_groq_api_key()
    if not api_key:
        st.session_state["last_groq_error"] = "Missing GROQ_API_KEY."
        return None
    payload = json.dumps(
        {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
    ).encode("utf-8")
    req = request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            st.session_state["last_groq_error"] = ""
            return content
    except error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8")
        except Exception:
            details = ""
        short_details = details[:220] if details else "No response body."
        st.session_state["last_groq_error"] = f"HTTP {exc.code}: {short_details}"
        return None
    except error.URLError as exc:
        st.session_state["last_groq_error"] = f"Network error: {exc.reason}"
        return None
    except TimeoutError:
        st.session_state["last_groq_error"] = "Request timed out while contacting Groq."
        return None
    except (KeyError, json.JSONDecodeError) as exc:
        st.session_state["last_groq_error"] = f"Invalid Groq response format: {exc}"
        return None
    except Exception as exc:
        st.session_state["last_groq_error"] = f"Unexpected Groq error: {exc}"
        return None


def _local_coach_reply(
    message: str,
    predicted_score: float | None,
    roadmap: dict[str, Any] | None,
    context_hits: list[dict[str, Any]] | None = None,
) -> str:
    msg = message.lower()
    tips = []
    context_hits = context_hits or []

    if any(k in msg for k in ["dsa", "data structure", "algorithm", "coding interview", "leetcode"]):
        dsa_plan = [
            "Week 1-2: Arrays, strings, hash maps, two pointers, sliding window.",
            "Week 3-4: Linked list, stack, queue, recursion, binary search patterns.",
            "Week 5-6: Trees, BST, heap/priority queue, graph BFS/DFS basics.",
            "Week 7-8: Dynamic programming (1D/2D), greedy, backtracking.",
            "Practice target: 2 medium + 3 easy problems per day, then 2 mocks/week.",
        ]
        tips.extend(dsa_plan)
        if context_hits:
            top_titles = [h.get("doc", {}).get("title", "") for h in context_hits[:2] if isinstance(h, dict)]
            top_titles = [t for t in top_titles if t]
            if top_titles:
                tips.append(f"Use these KB notes first: {', '.join(top_titles)}.")

    if predicted_score is not None:
        if predicted_score < 65:
            tips.append("Increase consistency: 90-minute focused sessions for 5 days/week.")
        elif predicted_score < 80:
            tips.append("Push from average to strong by adding weekly revision and one mock test.")
        else:
            tips.append("Keep momentum and focus on interview practice + portfolio quality.")
    if roadmap:
        tips.append(f"Follow roadmap milestone for month {min(2, len(roadmap['milestones']))} before adding new topics.")
    if "resume" in msg:
        tips.append("Prioritize impact bullets: action + metric + result.")
    if "interview" in msg:
        tips.append("Do 2 mock interviews/week: one technical, one behavioral.")
    if not tips:
        tips.append("Set one measurable goal for this week and review progress every Sunday.")
    return "\n".join([f"- {tip}" for tip in tips])


def _render_predict() -> None:
    st.subheader("Predict")
    st.caption("Estimate academic performance with factors, risks and cluster.")

    c1, c2 = st.columns(2)
    with c1:
        hours = st.slider("Hours Studied / week", 0.0, 50.0, 16.0, 0.5)
        attendance = st.slider("Attendance (%)", 50.0, 100.0, 82.0, 0.5)
        previous = st.slider("Previous average score", 40.0, 100.0, 75.0, 0.5)
    with c2:
        sleep = st.slider("Sleep (hours/day)", 4.0, 10.0, 7.0, 0.5)
        motivation = st.select_slider("Motivation", options=[1, 2, 3, 4, 5], value=3)

    if st.button("Run Prediction", type="primary", use_container_width=True):
        result = _predict_score(hours, attendance, previous, sleep, motivation)
        st.session_state["predict_result"] = result

    result = st.session_state.get("predict_result")
    if result:
        a, b, c = st.columns(3)
        a.metric("Predicted Score", f"{result['score']}/100")
        b.metric("Estimated Grade", result["grade"])
        c.metric("Cluster", result["cluster"])

        with st.expander("Factors"):
            for f in result["factors"]:
                st.write(f"- {f['label']}: {f['value']}")
        with st.expander("Risk Flags"):
            for r in result["risks"]:
                st.write(f"- {r['label']} ({r['level']})")


def _render_roadmap() -> None:
    st.subheader("Roadmap")
    st.caption("Generate a personalized roadmap with milestones and courses.")

    role = st.text_input("Dream role", value="Software Engineer")
    timeline = st.selectbox("Timeline", ["3 months", "6 months", "12 months"], index=1)
    weekly_hours = st.slider("Weekly hours available", 3, 30, 10)
    skills = st.text_input("Current skills (comma separated)", value="Python, SQL")
    context = st.text_area("Context / challenges", value="")

    if st.button("Generate Roadmap", use_container_width=True):
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        st.session_state["roadmap"] = _generate_roadmap(role, timeline, skill_list, weekly_hours, context)

    roadmap = st.session_state.get("roadmap")
    if roadmap:
        st.markdown("### Strategy")
        st.write(roadmap["summary"])
        st.write("Skills:", ", ".join(roadmap["skills"]) if roadmap["skills"] else "Not provided")
        if roadmap["context"]:
            st.write("Context:", roadmap["context"])
        st.markdown("### Timeline")
        for item in roadmap["milestones"]:
            st.write(f"- Month {item['month']}: {item['task']}")
            if item.get("topics"):
                st.write(f"  - Topics: {', '.join(item['topics'])}")
            if item.get("deliverable"):
                st.write(f"  - Deliverable: {item['deliverable']}")
            if item.get("interview_focus"):
                st.write(f"  - Interview focus: {item['interview_focus']}")
        if roadmap.get("weekly_plan"):
            st.markdown("### Weekly Execution Plan")
            for day_item in roadmap["weekly_plan"]:
                st.write(f"- {day_item['day']}: {day_item['focus']}")
        if roadmap.get("measurable_goals"):
            st.markdown("### Measurable Goals")
            for goal in roadmap["measurable_goals"]:
                st.write(f"- {goal}")
        st.markdown("### Recommended Courses")
        for course in roadmap["courses"]:
            st.write(f"- {course['name']} ({course['platform']}, {course['duration']})")
        if roadmap.get("certifications"):
            st.markdown("### Certifications")
            for cert in roadmap["certifications"]:
                st.write(f"- {cert}")


def _render_coach() -> None:
    st.subheader("AI Coach")
    st.caption("Agentic coach with RAG + tool calling (predict, roadmap, resume evaluation).")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Ask your coach anything...")
    if not user_prompt:
        return

    st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    predict_result = st.session_state.get("predict_result")
    roadmap = st.session_state.get("roadmap")
    coach_graph = _build_coach_rag_graph()
    rag_result = coach_graph.invoke(
        {
            "query": user_prompt,
            "predict_result": predict_result,
            "roadmap": roadmap,
        }
    )
    context_hits = rag_result.get("context_hits", [])
    reply = rag_result.get("reply", "I could not generate a response right now.")
    tool_result = rag_result.get("tool_result")
    llm_mode = rag_result.get("llm_mode", "local_fallback")
    llm_error = rag_result.get("llm_error", "")

    with st.chat_message("assistant"):
        st.markdown(reply)
        if llm_mode == "local_fallback":
            if llm_error:
                st.warning(f"Using local fallback response. Groq error: {llm_error}")
            else:
                st.warning("Using local fallback response. Groq request did not return content.")
        else:
            st.caption("Response source: Groq LLM")
        if tool_result and tool_result.get("ok"):
            st.caption(f"Tool used: {tool_result.get('tool_name')}")
        if context_hits:
            st.caption("Used knowledge base context:")
            for hit in context_hits:
                st.write(f"- {hit['doc']['title']} (score: {hit['score']:.2f})")
    st.session_state["chat_history"].append({"role": "assistant", "content": reply})


def _render_resume_eval() -> None:
    st.subheader("Resume Evaluation")
    st.caption("AI-powered ATS-style evaluation with rule-based fallback.")
    target_role = st.text_input("Target role", value="Software Engineer")
    resume_text = st.text_area("Paste resume text", height=260)
    if st.button("Evaluate Resume", use_container_width=True):
        if not resume_text.strip():
            st.warning("Please paste your resume text first.")
            return
        st.session_state["latest_resume_text"] = resume_text.strip()
        st.session_state["latest_resume_target_role"] = target_role.strip() or "Software Engineer"
        report = _evaluate_resume_ai(
            st.session_state["latest_resume_text"],
            st.session_state["latest_resume_target_role"],
        )
        st.success(report["verdict"])
        st.metric("Overall Score", f"{report['overall']}/100")
        st.markdown("### Strengths")
        for s in report["strengths"]:
            st.write(f"- {s}")
        st.markdown("### Gaps")
        for g in report["gaps"]:
            st.write(f"- {g}")


def _render_notes() -> None:
    st.subheader("Notes")
    st.caption("Save personal progress notes locally.")
    note = st.text_area("Write a note", height=150)
    save_path = DATA_DIR / "notes.json"

    if st.button("Save Note", use_container_width=True):
        payload = {"note": note.strip()}
        save_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        st.success("Note saved to data/notes.json")

    if save_path.exists():
        current = json.loads(save_path.read_text(encoding="utf-8"))
        st.info(f"Saved note: {current.get('note', '')}")


def _render_setup() -> None:
    st.subheader("Knowledge Base Setup")
    st.caption("Ingest custom notes/documents to improve coach responses.")
    default_text = "\n\n".join([f"{d['title']}\n{d['content']}" for d in _default_kb_docs()])
    kb_input = st.text_area("Knowledge documents (separate docs with blank lines)", value=default_text, height=230)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ingest Knowledge Base", use_container_width=True):
            count = _ingest_kb(kb_input)
            st.success(f"Ingested {count} documents into local knowledge base.")
    with c2:
        if st.button("Load default KB", use_container_width=True):
            KB_FILE.write_text(json.dumps(_default_kb_docs(), indent=2), encoding="utf-8")
            _rebuild_vector_index_from_kb()
            st.success("Loaded default knowledge base.")
    docs = _load_kb()
    st.write(f"Current KB documents: {len(docs)}")
    st.caption(
        "Retrieval mode: "
        + ("Embedding + Vector DB (Chroma)" if _vector_db_available() else "Lexical fallback (install vector deps)")
    )


def main() -> None:
    st.title("AcadPipeline - Streamlit")
    st.caption("Standalone app with prediction, roadmap, coach, resume evaluation, and KB retrieval.")

    page = st.sidebar.radio("Navigation", ["Predict", "Roadmap", "AI Coach", "Resume Evaluation", "Knowledge Base", "Notes"])
    st.sidebar.write(f"GROQ key configured: {'Yes' if bool(_get_groq_api_key()) else 'No'}")
    if not _vector_db_available():
        st.sidebar.warning(
            "Embedding retrieval is unavailable in this runtime. "
            "Coach will use lexical fallback retrieval until ML dependencies are installed."
        )
    if page == "Predict":
        _render_predict()
    elif page == "Roadmap":
        _render_roadmap()
    elif page == "AI Coach":
        _render_coach()
    elif page == "Resume Evaluation":
        _render_resume_eval()
    elif page == "Knowledge Base":
        _render_setup()
    else:
        _render_notes()


if __name__ == "__main__":
    main()
