# AcadPipeline

AcadPipeline is a full-stack career guidance platform for students, combining predictive analytics, LLM-generated planning, and agentic coaching.

## Core Capabilities

- `Predict`: ML-based academic score prediction with factor and risk analysis.
- `Roadmap`: Structured career roadmap generation tailored to user profile and goals.
- `AI Coach`: LangGraph-powered chat agent with tool calling for prediction, roadmap generation, resume evaluation, and retrieval-augmented guidance (RAG).
- `Authentication`: Cookie-based auth with optional Mongo-backed persistence for user context and chat history.

## Tech Stack

- Frontend: React, TypeScript, Vite, Zustand
- Backend: FastAPI, Pydantic, Motor (MongoDB), scikit-learn
- LLM: Groq API
- Agent Orchestration: LangGraph + LangChain tools
- RAG: ChromaDB + sentence-transformers embeddings

## Repository Structure

```text
backend/
  main.py
  routers/
  services/
  models/
  db/
  security/
  tests/
  scripts/
  knowledge_base/
frontend/
  src/
  package.json
render.yaml
DEPLOYMENT.md
```

## Local Development

### 1) Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_models.py
PYTHONPATH=. python scripts/ingest_kb.py
uvicorn main:app --reload
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Configuration

Use the example files as templates:

- `backend/.env.example`
- `frontend/.env.example`

Minimum backend variables:

- `GROQ_API_KEY`
- `JWT_SECRET`
- `MONGO_URL` (for auth/session persistence)
- `FRONTEND_ORIGIN`

For cross-domain production cookies (Vercel frontend + Render backend):

- `COOKIE_SECURE=true`
- `COOKIE_SAMESITE=none`

## Deployment

- Backend target: Render (`backend/`, configured via `render.yaml`)
- Frontend target: Vercel (`frontend/`, configured via `frontend/vercel.json`)

See `DEPLOYMENT.md` for step-by-step deployment instructions.

## Testing

From `backend/`:

```bash
PYTHONPATH=. pytest tests/ -q
```

## Notes

- Trained model artifacts are stored under `backend/models/ml_models/`.
- Chroma persistent storage defaults to `backend/data/chroma/`.
- Seed knowledge documents are in `backend/knowledge_base/seed_documents.json`.

