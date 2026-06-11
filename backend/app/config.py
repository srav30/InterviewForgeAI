from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    interviewer_model: str = "gpt-4o-mini"
    cors_origins: str = (
        "http://localhost:3000,https://interview-forge-ai-omega.vercel.app"
    )
    cors_origin_regex: str = r"https://.*\.vercel\.app"
    chroma_path: str = str(BACKEND_ROOT / "data" / "chroma")
    chroma_collection: str = "interview_content"
    embedding_model: str = "text-embedding-3-small"
    ingest_on_startup: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
