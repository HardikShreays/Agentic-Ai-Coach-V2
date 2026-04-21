# AcadPipeline

AcadPipeline is an agentic student-success platform built with Streamlit. It combines predictive analytics, roadmap planning, retrieval-augmented coaching, and resume intelligence into a single workflow designed for academic and early-career outcomes.

## Executive Summary

AcadPipeline provides a modular experience across six capabilities:

- `Predict`: rule-based score prediction with explainable factors, grade mapping, cluster labeling, and risk flags.
- `Roadmap`: timeline-driven role preparation plans with milestones and measurable execution goals.
- `AI Coach`: conversational guidance that uses retrieval, session context, optional tool-calling, and LLM fallback logic.
- `Resume Evaluation`: ATS-style structure and impact analysis with strengths/gaps output.
- `Knowledge Base`: in-app document ingestion and retrieval indexing for domain-specific coaching context.
- `Notes`: local persistence for user-specific progress tracking.

The architecture is intentionally hybrid:
- deterministic components for reliability and explainability,
- optional LLM augmentation for richer coaching quality,
- graceful fallback for degraded network/provider conditions.

## System Architecture

### High-Level Components

1. **Presentation Layer**
   - Streamlit UI (`streamlit_app.py`) renders feature pages and interactive widgets.
   - Sidebar navigation acts as module router.

2. **Application Layer**
   - Feature-specific render handlers (`_render_predict`, `_render_roadmap`, `_render_coach`, etc.).
   - Session-aware state management via `st.session_state`.

3. **Intelligence Layer**
   - Rule engines:
     - prediction scoring and risk heuristics,
     - roadmap template generation,
     - resume quality scoring.
   - Agent pipeline (LangGraph):
     - retrieval node,
     - planning node,
     - conditional tool execution node,
     - response generation node.
   - Optional LLM provider (Groq Chat Completions) with robust fallback.

4. **Data Layer**
   - Local JSON persistence (`data/knowledge_base.json`, notes).
   - Optional vector retrieval (Chroma + Sentence Transformers embeddings).
   - Lexical retrieval fallback (Jaccard similarity) when vector services are unavailable.

## AI Coach Execution Flow

For each user message:

1. **Input capture**  
   User prompt is appended to chat history.

2. **Context retrieval**  
   Top-k context chunks are retrieved from vector DB (or lexical fallback).

3. **Planning step**  
   A planner prompt decides whether to:
   - call a tool (`predict_score`, `generate_roadmap`, `evaluate_resume_ai`, etc.), or
   - directly respond.

4. **Tool execution (conditional)**  
   Selected tool executes with validated/normalized arguments; outputs are synced to session state.

5. **Response generation**  
   The responder uses:
   - current user prompt,
   - last 5 chat messages,
   - predicted score context,
   - roadmap context,
   - retrieval context,
   - tool output context.

6. **Failover handling**  
   If Groq is unavailable/blocked/rate-limited, the app returns a local structured coaching response and surfaces the failure reason in UI.

## Data and State Model

- **Transient Session State (`st.session_state`)**
  - `chat_history`
  - `predict_result`
  - `roadmap`
  - last provider error diagnostics

- **Persistent Local Data (`data/`)**
  - `knowledge_base.json`
  - `notes.json`
  - `vector_db/` (Chroma index files)

This split keeps runtime interactions responsive while preserving user-authored artifacts across restarts.

## Explainability and Reliability Design

- Prediction logic is deterministic and interpretable (weighted factors + thresholds).
- Risk flags are explicit and user-readable.
- Resume scoring is traceable to sections/metrics/structure checks.
- Coach responses remain functional without external LLM connectivity.
- Retrieval supports semantic mode when available, lexical fallback otherwise.

## Project Structure

- `streamlit_app.py` - entrypoint and full application logic
- `requirements.txt` - Python dependencies
- `.env` - optional local secrets
- `.streamlit/config.toml` - Streamlit runtime configuration
- `data/` - persisted runtime artifacts
  - `knowledge_base.json`
  - `notes.json`
  - `vector_db/`

## Technology Stack

- **Frontend/App Runtime:** Streamlit
- **Language:** Python 3.x
- **Orchestration:** LangGraph
- **Tool Interface:** LangChain tools
- **Retrieval Store:** ChromaDB (persistent local collection)
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **LLM Provider (optional):** Groq Chat Completions API

## Setup and Run

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Configure environment

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key
```

For deployed Streamlit, prefer secrets configuration (`st.secrets`) with the same key name.

### 3) Start application

```bash
streamlit run streamlit_app.py
```

## Deployment Notes

- The application supports both:
  - environment variable loading (`GROQ_API_KEY`), and
  - Streamlit secrets lookup.
- If provider calls fail, UI surfaces actionable diagnostics (HTTP/network/timeout/format errors).
- In provider-denied environments (for example `HTTP 403` edge/firewall blocks), local fallback remains available.

## Troubleshooting

- **Coach replies are generic**
  - Verify coach warning/caption source.
  - Check displayed provider error details.
  - Confirm deployment secrets include valid `GROQ_API_KEY`.

- **Retrieval quality is weak**
  - Re-ingest domain knowledge in Knowledge Base page.
  - Ensure embedding dependencies are installed and vector index builds successfully.

- **Dependency import warnings in editor**
  - Ensure active interpreter/virtual environment matches `requirements.txt`.

## Security and Operational Considerations

- Never commit real API keys.
- Treat local `data/` as user-generated data; apply retention/backup policy as needed.
- For multi-user production usage, move persistence from local files to managed storage and add authentication controls.

## Roadmap (Recommended Next Enhancements)

- Provider failover chain (Groq -> secondary provider -> local fallback).
- Token-aware memory compaction/summarization for long conversations.
- Evaluation harness for coach response quality and regressions.
- Optional backend service split for stricter production controls and observability.

