from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import streamlit as st
from urllib import error, request

st.set_page_config(page_title="AcadPipeline", page_icon="🎓", layout="wide")

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
KB_FILE = DATA_DIR / "knowledge_base.json"
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


def _ingest_kb(raw_text: str) -> int:
    blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
    docs: list[dict[str, str]] = []
    for i, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        title = lines[0][:80].strip() or f"Document {i}"
        docs.append({"title": title, "content": block})
    KB_FILE.write_text(json.dumps(docs, indent=2), encoding="utf-8")
    return len(docs)


def _retrieve_context(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    docs = _load_kb()
    ranked = sorted(
        [{"doc": d, "score": _jaccard_score(query, d["content"])} for d in docs],
        key=lambda x: x["score"],
        reverse=True,
    )
    return [r for r in ranked[:top_k] if r["score"] > 0.0]


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
    milestones = []
    for month in range(1, months + 1):
        if month == 1:
            item = "Set foundation and revise core concepts."
        elif month <= months // 2:
            item = "Build guided projects and practice interviews."
        elif month < months:
            item = "Ship portfolio project and strengthen resume."
        else:
            item = "Apply strategically and run mock interviews."
        milestones.append({"month": month, "task": item})
    courses = [
        {"name": "Data Structures and Algorithms", "platform": "LeetCode / GFG", "duration": "8 weeks"},
        {"name": f"{role} Fundamentals", "platform": "Coursera / YouTube", "duration": "6 weeks"},
        {"name": "System Design Basics", "platform": "Educative", "duration": "4 weeks"},
    ]
    return {
        "summary": f"Focused {timeline} plan for {role} with about {weekly_hours} hours/week.",
        "skills": skills,
        "context": context,
        "milestones": milestones,
        "courses": courses,
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


def _groq_chat(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
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
            return data["choices"][0]["message"]["content"]
    except (error.URLError, error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError):
        return None


def _local_coach_reply(message: str, predicted_score: float | None, roadmap: dict[str, Any] | None) -> str:
    tips = []
    if predicted_score is not None:
        if predicted_score < 65:
            tips.append("Increase consistency: 90-minute focused sessions for 5 days/week.")
        elif predicted_score < 80:
            tips.append("Push from average to strong by adding weekly revision and one mock test.")
        else:
            tips.append("Keep momentum and focus on interview practice + portfolio quality.")
    if roadmap:
        tips.append(f"Follow roadmap milestone for month {min(2, len(roadmap['milestones']))} before adding new topics.")
    if "resume" in message.lower():
        tips.append("Prioritize impact bullets: action + metric + result.")
    if "interview" in message.lower():
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
        st.markdown("### Recommended Courses")
        for course in roadmap["courses"]:
            st.write(f"- {course['name']} ({course['platform']}, {course['duration']})")


def _render_coach() -> None:
    st.subheader("AI Coach")
    st.caption("Context-aware coach with local retrieval and optional GROQ response.")
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

    context_hits = _retrieve_context(user_prompt)
    context_text = "\n".join(
        [f"{idx+1}. {hit['doc']['title']}: {hit['doc']['content']}" for idx, hit in enumerate(context_hits)]
    )
    predict_result = st.session_state.get("predict_result")
    roadmap = st.session_state.get("roadmap")

    system_prompt = (
        "You are a concise career coach for college students. "
        "Give practical next steps and avoid generic motivation-only advice."
    )
    user_context = (
        f"User message: {user_prompt}\n"
        f"Predicted score context: {predict_result}\n"
        f"Roadmap context: {roadmap}\n"
        f"Knowledge context:\n{context_text}"
    )
    llm_reply = _groq_chat(system_prompt, user_context)
    reply = llm_reply or _local_coach_reply(
        user_prompt,
        predict_result["score"] if predict_result else None,
        roadmap,
    )

    with st.chat_message("assistant"):
        st.markdown(reply)
        if context_hits:
            st.caption("Used knowledge base context:")
            for hit in context_hits:
                st.write(f"- {hit['doc']['title']} (score: {hit['score']:.2f})")
    st.session_state["chat_history"].append({"role": "assistant", "content": reply})


def _render_resume_eval() -> None:
    st.subheader("Resume Evaluation")
    st.caption("Structured ATS-style evaluation with strengths and gaps.")
    target_role = st.text_input("Target role", value="Software Engineer")
    resume_text = st.text_area("Paste resume text", height=260)
    if st.button("Evaluate Resume", use_container_width=True):
        if not resume_text.strip():
            st.warning("Please paste your resume text first.")
            return
        report = _evaluate_resume(resume_text, target_role)
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
            st.success("Loaded default knowledge base.")
    docs = _load_kb()
    st.write(f"Current KB documents: {len(docs)}")


def main() -> None:
    st.title("AcadPipeline - Streamlit")
    st.caption("Standalone app with prediction, roadmap, coach, resume evaluation, and KB retrieval.")

    page = st.sidebar.radio("Navigation", ["Predict", "Roadmap", "AI Coach", "Resume Evaluation", "Knowledge Base", "Notes"])
    st.sidebar.write(f"GROQ key configured: {'Yes' if bool(os.getenv('GROQ_API_KEY')) else 'No'}")
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
