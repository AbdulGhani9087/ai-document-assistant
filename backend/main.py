"""
main.py — FastAPI application entry point.
Run with:  uvicorn main:app --reload
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import documents, chat

# ── Ensure required directories exist on startup ──────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    print(f"[OK] DocChat {settings.app_version} starting [{settings.environment}]")
    print(f"    Embedding model : {settings.embedding_model}")
    print(f"    LLM             : {settings.groq_model_name} (via Groq)")
    print(f"    Vector store    : {settings.chroma_persist_dir}")
    print(f"    Database        : {settings.database_url}")
    yield
    print("[STOP] DocChat shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"DocChat API",
    version=settings.app_version,
    description="AI Document Assistant — RAG-powered Q&A over uploaded documents.",
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "DocChat API",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "ok",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,
    )
