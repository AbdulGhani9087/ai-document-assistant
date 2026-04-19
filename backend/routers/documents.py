"""
routers/documents.py — Document upload, list, and delete endpoints.
"""
from __future__ import annotations

import os
import uuid
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from config import settings
from document_loader import load_document
from chunking import chunk_text
from chroma_client import store_chunks, delete_document

router = APIRouter()

# ── Pydantic models ───────────────────────────────────────────────────────────

class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    session_id: str
    size_bytes: int
    chunk_count: int


# In-memory store for demo (swap for DB in production)
_docs: dict[str, DocumentMeta] = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentMeta)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
):
    # --- Validate MIME type ---
    if file.content_type not in settings.allowed_mime_list:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # --- Validate file size ---
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max is {settings.max_upload_size_mb} MB.",
        )

    # --- Save to disk ---
    doc_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    # --- Extract text ---
    text = load_document(save_path, file.content_type)

    # --- Chunk & embed ---
    chunks = chunk_text(text)
    store_chunks(doc_id=doc_id, session_id=session_id, chunks=chunks)

    meta = DocumentMeta(
        doc_id=doc_id,
        filename=file.filename,
        session_id=session_id,
        size_bytes=len(contents),
        chunk_count=len(chunks),
    )
    _docs[doc_id] = meta
    return meta


@router.get("/{session_id}", response_model=list[DocumentMeta])
async def list_documents(session_id: str):
    return [d for d in _docs.values() if d.session_id == session_id]


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    if doc_id not in _docs:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(doc_id)
    _docs.pop(doc_id)
    return {"detail": "deleted", "doc_id": doc_id}
