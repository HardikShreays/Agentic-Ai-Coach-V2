import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.predict import router as predict_router
from routers.roadmap import router as roadmap_router
from routers.coach import router as coach_router
from routers.auth import router as auth_router
from services.ml_engine import init_models
from services.rag_service import ingest_seed_knowledge_base
from db.mongo import create_mongo_client, get_database


load_dotenv()

app = FastAPI(title="AcadPipeline v2 Backend")


if os.getenv("ENABLE_CORS", "true").lower() in {"1", "true", "yes"}:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def _startup() -> None:
    # Load ML models (if trained artifacts exist) or leave None for fallback mode.
    init_models()

    # MongoDB (optional until you enable signup/login)
    mongo_url = os.getenv("MONGO_URL")
    if mongo_url:
        client = create_mongo_client()
        app.state.mongo_client = client
        app.state.db = get_database(client)
    else:
        app.state.mongo_client = None
        app.state.db = None

    if os.getenv("INGEST_KB_ON_STARTUP", "false").lower() in {"1", "true", "yes"}:
        ingest_seed_knowledge_base()


@app.on_event("shutdown")
def _shutdown() -> None:
    client = getattr(app.state, "mongo_client", None)
    if client is not None:
        client.close()


app.include_router(predict_router, prefix="/api", tags=["predict"])
app.include_router(roadmap_router, prefix="/api", tags=["roadmap"])
app.include_router(coach_router, prefix="/api", tags=["coach"])
app.include_router(auth_router, prefix="/api", tags=["auth"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "port": int(os.getenv("PORT", "8000"))}

