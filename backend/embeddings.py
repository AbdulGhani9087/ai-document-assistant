"""
embeddings.py — Generate dense vector embeddings via Hugging Face sentence-transformers.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from config import settings


@lru_cache(maxsize=1)
def _get_embedding_model() -> HuggingFaceEmbeddings:
    """Load the embedding model once and cache it for the process lifetime."""
    model_kwargs = {}
    encode_kwargs = {"normalize_embeddings": True}

    if settings.hf_token:
        model_kwargs["token"] = settings.hf_token

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )


def generate_embedding(text: str) -> list[float]:
    """Return the embedding vector for a single text string."""
    model = _get_embedding_model()
    return model.embed_query(text)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors for a list of text strings."""
    model = _get_embedding_model()
    return model.embed_documents(texts)
