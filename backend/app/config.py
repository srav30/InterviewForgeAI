from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    interviewer_model: str = "gpt-4o-mini"
    cors_origins: str = (
        "http://localhost:3000,https://interview-forge-ai-omega.vercel.app"
    )
    cors_origin_regex: str = r"https://.*\.vercel\.app"


@lru_cache
def get_settings() -> Settings:
    return Settings()
