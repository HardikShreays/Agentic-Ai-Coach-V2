from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Allow importing existing backend modules directly.
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _load_backend_env() -> None:
    """
    Load env vars from backend/.env.
    Uses python-dotenv if available; otherwise falls back to a simple parser
    so Streamlit can run even when dotenv isn't installed.
    """
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        return

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(env_path)
        return
    except Exception:
        pass

    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Keep app running even if env file parsing fails.
        return


_load_backend_env()

from models.schemas import CoachRequest, PredictRequest, RoadmapRequest, SessionContext  # noqa: E402
from services.coach_agent import run_coach_agent_sync  # noqa: E402
from services.ml_engine import init_models, predict  # noqa: E402
from services.prompt_builder import build_coach_agent_system_prompt  # noqa: E402
from services.rag_service import ingest_seed_knowledge_base  # noqa: E402
from services.resume_eval_service import evaluate_resume_structured  # noqa: E402
from services.roadmap_service import generate_roadmap  # noqa: E402


st.set_page_config(page_title="AcadPipeline Streamlit", page_icon="🎓", layout="wide")


def _init_session_state() -> None:
    if "models_ready" not in st.session_state:
        init_models()
        st.session_state.models_ready = True
    if "kb_ingested" not in st.session_state:
        st.session_state.kb_ingested = False
    if "last_predict_inputs" not in st.session_state:
        st.session_state.last_predict_inputs = None
    if "last_predict_result" not in st.session_state:
        st.session_state.last_predict_result = None
    if "last_roadmap_inputs" not in st.session_state:
        st.session_state.last_roadmap_inputs = None
    if "last_roadmap_result" not in st.session_state:
        st.session_state.last_roadmap_result = None
    if "coach_history" not in st.session_state:
        st.session_state.coach_history = []
    if "session_context" not in st.session_state:
        st.session_state.session_context = SessionContext()


def _sync_context_from_predict(result: Any) -> None:
    st.session_state.session_context = SessionContext(
        predicted_score=result.score,
        grade=result.grade,
        cluster_label=result.cluster_label,
        risk_flags=[r.label for r in result.risks],
        target_role=st.session_state.session_context.target_role,
        timeline=st.session_state.session_context.timeline,
    )


def _sync_context_from_roadmap(req: RoadmapRequest) -> None:
    st.session_state.session_context = SessionContext(
        predicted_score=st.session_state.session_context.predicted_score,
        grade=st.session_state.session_context.grade,
        cluster_label=st.session_state.session_context.cluster_label,
        risk_flags=st.session_state.session_context.risk_flags,
        target_role=req.dream_role,
        timeline=req.timeline,
    )


def _render_predict_page() -> None:
    st.subheader("Predict: Academic Score")
    st.caption("ML-based score prediction with factors, risks, and peer cluster.")

    with st.form("predict_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            hours_studied = st.slider("Hours Studied", 0.0, 44.0, 18.0, 0.5)
            attendance = st.slider("Attendance (%)", 60.0, 100.0, 85.0, 0.5)
            previous_scores = st.slider("Previous Scores", 50.0, 100.0, 78.0, 0.5)
        with c2:
            sleep_hours = st.slider("Sleep Hours", 4.0, 10.0, 7.0, 0.5)
            tutoring_sessions = st.slider("Tutoring Sessions", 0.0, 8.0, 2.0, 0.5)
            parental_involvement = st.selectbox("Parental Involvement", [1, 2, 3], index=1)
        with c3:
            access_to_resources = st.selectbox("Access to Resources", [1, 2, 3], index=1)
            motivation_level = st.selectbox("Motivation Level", [1, 2, 3], index=1)
            internet_access = st.selectbox("Internet Access", [0, 1], index=1)

        submit = st.form_submit_button("Run Prediction", use_container_width=True)

    if submit:
        req = PredictRequest(
            hours_studied=hours_studied,
            attendance=attendance,
            previous_scores=previous_scores,
            sleep_hours=sleep_hours,
            tutoring_sessions=tutoring_sessions,
            parental_involvement=parental_involvement,
            access_to_resources=access_to_resources,
            motivation_level=motivation_level,
            internet_access=internet_access,
        )
        result = predict(req)
        st.session_state.last_predict_inputs = req.model_dump()
        st.session_state.last_predict_result = result
        _sync_context_from_predict(result)

    result = st.session_state.last_predict_result
    if result is None:
        return

    a, b, c = st.columns(3)
    a.metric("Predicted Score", f"{result.score:.1f}/100")
    b.metric("Grade", f"{result.grade} ({result.grade_label})")
    c.metric("Cluster", result.cluster_label)

    st.write(result.cluster_description)

    with st.expander("Factors"):
        for f in result.factors:
            st.write(f"- {f.label}: {f.value:.1f}")
    with st.expander("Risk Flags"):
        for r in result.risks:
            st.write(f"- {r.label} ({r.level})")


def _render_roadmap_page() -> None:
    st.subheader("Roadmap: Career Planning")
    st.caption("Generates a personalized India-focused roadmap from your profile.")

    with st.form("roadmap_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", value="Student")
            stage = st.selectbox("Stage", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"])
            field = st.text_input("Field / Branch", value="Computer Science")
            score = st.text_input("Academic Score (optional)", value="")
        with c2:
            dream_role = st.text_input("Dream Role", value="Software Engineer")
            timeline = st.selectbox("Timeline", ["3 months", "6 months", "12 months", "18 months"])
            weekly_hours = st.selectbox("Weekly Hours Available", ["5", "8", "10", "15", "20"])
            skills_text = st.text_area("Skills (comma separated)", value="Python, DSA")
        context = st.text_area("Context / Challenges (optional)", value="")
        submit = st.form_submit_button("Generate Roadmap", use_container_width=True)

    if submit:
        skills = [s.strip() for s in skills_text.split(",") if s.strip()]
        req = RoadmapRequest(
            name=name.strip() or "Student",
            stage=stage,
            field=field.strip() or "General",
            score=score.strip() or None,
            skills=skills or ["Communication"],
            dream_role=dream_role.strip() or "Software Engineer",
            timeline=timeline,
            weekly_hours=weekly_hours,
            context=context.strip() or None,
        )
        with st.spinner("Generating roadmap..."):
            result = generate_roadmap(req)
        st.session_state.last_roadmap_inputs = req.model_dump()
        st.session_state.last_roadmap_result = result
        _sync_context_from_roadmap(req)

    result = st.session_state.last_roadmap_result
    if result is None:
        return

    st.markdown("### Strategy")
    st.write(result.summary)

    st.markdown("### Skill Gaps")
    for gap in result.skill_gaps:
        st.write(f"- {gap.skill}: {gap.current}/100 -> {gap.required}/100 ({gap.priority})")

    st.markdown("### Timeline")
    for t in result.timeline:
        st.write(f"- {t.month}: {t.emoji} **{t.title}** - {t.description}")

    st.markdown("### Courses")
    for course in result.courses:
        st.write(f"- {course.name} ({course.platform}, {course.duration}, {course.type})")

    st.markdown("### Internship Strategy")
    for i in result.internships:
        st.write(f"- {i.emoji} **{i.title}** via {i.platform}: {i.tips}")

    st.markdown("### Resume Tips")
    for tip in result.resume_tips:
        st.write(f"- {tip}")


def _render_coach_page() -> None:
    st.subheader("AI Coach")
    st.caption("LangGraph coach using your saved prediction and roadmap context.")

    topic = st.selectbox("Topic", ["career", "skills", "interview", "resume", "motivation"], index=0)
    resume_text = st.text_area("Optional resume text for this chat turn", value="", height=140)

    for msg in st.session_state.coach_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your coach...")
    if not user_input:
        return

    st.session_state.coach_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            req = CoachRequest(
                message=user_input,
                history=[],
                topic=topic,
                session_context=st.session_state.session_context,
                resume_text=resume_text.strip() or None,
            )
            try:
                reply, effects = run_coach_agent_sync(
                    system_prompt=build_coach_agent_system_prompt(
                        topic,
                        st.session_state.session_context,
                        req.resume_text,
                    ),
                    messages=st.session_state.coach_history,
                    last_predict_inputs=st.session_state.last_predict_inputs,
                    last_roadmap_inputs=st.session_state.last_roadmap_inputs,
                    resume_text_default=req.resume_text,
                )
            except Exception as e:
                reply = f"Coach error: {e}"
                effects = {}

            # Keep local state aligned when tools are called by agent.
            if "predict_refresh" in effects:
                st.session_state.last_predict_inputs = effects["predict_refresh"]["request"]
            if "roadmap_refresh" in effects:
                st.session_state.last_roadmap_inputs = effects["roadmap_refresh"]["request"]

            st.markdown(reply)
            st.session_state.coach_history.append({"role": "assistant", "content": reply})


def _render_resume_eval_page() -> None:
    st.subheader("Resume Evaluation")
    st.caption("Structured ATS/placement-style resume review.")

    target_role = st.text_input("Target role (optional)", value="")
    field = st.text_input("Field / branch (optional)", value="")
    resume_text = st.text_area("Paste resume text", height=260)

    if st.button("Evaluate Resume", use_container_width=True):
        if not resume_text.strip():
            st.warning("Please paste resume text first.")
            return
        with st.spinner("Evaluating..."):
            ev = evaluate_resume_structured(
                resume_text.strip(),
                target_role=target_role.strip() or None,
                field=field.strip() or None,
            )
        st.success(ev.one_line_verdict)
        c1, c2, c3 = st.columns(3)
        c1.metric("Overall", ev.overall_score)
        c2.metric("Format", ev.format_score)
        c3.metric("Content", ev.content_score)

        st.markdown("### Strengths")
        for s in ev.strengths:
            st.write(f"- {s}")
        st.markdown("### Gaps")
        for g in ev.gaps:
            st.write(f"- {g}")
        st.markdown("### Prioritized Fixes")
        for i, fix in enumerate(ev.prioritized_fixes, start=1):
            st.write(f"{i}. {fix}")


def main() -> None:
    _init_session_state()

    st.title("AcadPipeline - Streamlit Edition")
    st.caption("Single-app project for college assignment (Predict + Roadmap + Coach + Resume).")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Predict", "Roadmap", "AI Coach", "Resume Evaluation"],
            label_visibility="collapsed",
        )
        st.divider()
        st.subheader("Setup")
        st.write(f"GROQ key set: {'Yes' if bool(os.getenv('GROQ_API_KEY')) else 'No'}")
        if st.button("Ingest Knowledge Base", use_container_width=True):
            with st.spinner("Ingesting KB..."):
                count = ingest_seed_knowledge_base()
            st.session_state.kb_ingested = True
            st.success(f"Ingested {count} chunks into Chroma.")

    if page == "Predict":
        _render_predict_page()
    elif page == "Roadmap":
        _render_roadmap_page()
    elif page == "AI Coach":
        _render_coach_page()
    else:
        _render_resume_eval_page()


if __name__ == "__main__":
    main()
