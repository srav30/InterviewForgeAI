from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.rag.ingest import ingest_if_empty
from app.routes.interview import router as interview_router

settings = get_settings()
cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    chunks_ingested = ingest_if_empty()
    if chunks_ingested:
        print(f"Ingested {chunks_ingested} question/rubric chunks into ChromaDB")
    yield


app = FastAPI(title="InterviewForge AI", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
