"""
config.py — centralised settings loaded from .env via pydantic-settings.
Every module imports `settings` from here instead of calling os.getenv().
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",          # load from backend/.env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model_name: str = Field("llama2-70b-4096", description="Groq model id")

    # ── Hugging Face ─────────────────────────────────────────────────────────
    hf_token: str = Field("", description="HF token (blank = public models only)")
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="HF embedding model name",
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_dir: str = Field("./chroma_store")
    chroma_collection_name: str = Field("docchat_docs")

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field("sqlite:///./docchat.db")

    # ── Server ───────────────────────────────────────────────────────────────
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    allowed_origins: str = Field("http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ── Upload ───────────────────────────────────────────────────────────────
    max_upload_size_mb: int = Field(100000)
    upload_dir: str = Field("./uploads")
    allowed_mime_types: str = Field(
        "application/pdf,"
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
        "text/plain"
    )

    @property
    def allowed_mime_list(self) -> List[str]:
        return [m.strip() for m in self.allowed_mime_types.split(",") if m.strip()]

    # ── RAG Parameters ───────────────────────────────────────────────────────
    chunk_size: int = Field(400)
    chunk_overlap: int = Field(50)
    top_k_results: int = Field(5)

    # ── Security ─────────────────────────────────────────────────────────────
    secret_key: str = Field(..., description="App secret key")
    access_token_expire_minutes: int = Field(1440)

    # ── App ──────────────────────────────────────────────────────────────────
    environment: str = Field("development")
    enable_api_docs: bool = Field(True)
    app_version: str = Field("1.0.0")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()


# Convenient module-level alias
settings = get_settings()
