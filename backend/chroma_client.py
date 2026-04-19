"""
chroma_client.py — ChromaDB vector store interactions.
"""
from __future__ import annotations

import chromadb
from chromadb.config import Settings as ChromaSettings
from functools import lru_cache

from config import settings
from embeddings import generate_embedding, generate_embeddings


@lru_cache(maxsize=1)
def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )


# ── Write ─────────────────────────────────────────────────────────────────────

def store_chunks(
    doc_id: str,
    session_id: str,
    chunks: list[str],
) -> None:
    """Embed and store a list of text chunks in ChromaDB."""
    collection = _get_collection()

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    embeddings = generate_embeddings(chunks)
    metadatas = [
        {"doc_id": doc_id, "session_id": session_id, "chunk_index": i}
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


# ── Read ──────────────────────────────────────────────────────────────────────

def search(
    query: str,
    session_id: str | None = None,
    doc_id: str | None = None,
    top_k: int | None = None,
) -> list[str]:
    """
    Semantic similarity search.
    Optionally filter by session_id and doc_id so answers come from the right documents.
    """
    collection = _get_collection()
    k = top_k or settings.top_k_results
    query_embedding = generate_embedding(query)

    where = None
    if session_id and doc_id:
        where = {"$and": [{"session_id": session_id}, {"doc_id": doc_id}]}
    elif session_id:
        where = {"session_id": session_id}
    elif doc_id:
        where = {"doc_id": doc_id}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=["documents"],
    )
    return results["documents"][0] if results["documents"] else []


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_document(doc_id: str) -> None:
    """Remove all chunks belonging to a document."""
    collection = _get_collection()
    collection.delete(where={"doc_id": doc_id})
