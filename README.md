# AcadPipeline

AcadPipeline is a standalone Streamlit application designed to support students with academic and career decision-making in one unified workspace. The app combines performance prediction, roadmap planning, AI coaching, resume evaluation, and a lightweight local knowledge base to deliver practical, action-oriented guidance.

## Project Overview

The project is built as a single-app experience with a clean and maintainable structure. It is optimized for fast local setup, clear navigation, and feature-level modularity inside the Streamlit application.

Core goals:
- provide personalized academic and career guidance,
- keep usage simple and accessible through a single interface,
- support both offline-friendly logic and optional LLM-powered responses.

## Key Features

- **Academic Performance Prediction**
  - Estimates score and grade from study profile inputs.
  - Provides peer-style cluster labeling and risk indicators.
  - Displays interpretable factor breakdowns for transparency.

- **Career Roadmap Generation**
  - Builds role-focused plans across selected timelines.
  - Produces milestone-based execution steps.
  - Recommends targeted learning tracks and courses.

- **AI Coach**
  - Chat-based guidance for academics, skills, interviews, and resume strategy.
  - Uses saved app context (prediction + roadmap) for personalized replies.
  - Supports optional GROQ integration via `GROQ_API_KEY` with local fallback logic.

- **Resume Evaluation**
  - Performs structured ATS-style checks.
  - Generates an overall score, verdict, strengths, and improvement gaps.
  - Encourages measurable impact and role alignment.

- **Local Knowledge Base**
  - Ingests custom documents directly in-app.
  - Uses lightweight retrieval to surface relevant context for coaching.
  - Stores knowledge locally in `data/knowledge_base.json`.

## Tech Stack

- **Framework:** Streamlit
- **Language:** Python
- **Optional AI Provider:** GROQ Chat Completions API
- **Storage:** Local JSON files under `data/`

## Project Structure

- `streamlit_app.py` - main application entry point and feature modules
- `.streamlit/config.toml` - Streamlit runtime configuration
- `requirements.txt` - Python dependencies
- `data/` - local persisted files (knowledge base, notes, etc.)

## Environment Configuration

Create a root `.env` file (same level as `streamlit_app.py`) for secrets and runtime variables.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

The app auto-loads `.env` at startup and safely falls back if optional packages are unavailable.

## Getting Started

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run the application:
   - `streamlit run streamlit_app.py`

## Usage Flow

1. Start with **Predict** to estimate your current academic trajectory.
2. Use **Roadmap** to generate a structured goal plan.
3. Open **AI Coach** for context-aware, actionable guidance.
4. Run **Resume Evaluation** to identify strengths and critical fixes.
5. Use **Knowledge Base** to ingest custom notes and improve coaching quality.

## Notes

- All persisted data is stored locally.
- The app works without external AI services; LLM features become richer when `GROQ_API_KEY` is configured.
- This project is suitable for demos, academic projects, and iterative feature expansion.

