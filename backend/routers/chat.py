"""
routers/chat.py — Chat query and history endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from chroma_client import search
from llm_service import generate_answer

router = APIRouter()

# ── Pydantic models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    session_id: str
    doc_id: str | None = None


class Message(BaseModel):
    role: str          # "user" | "assistant"
    content: str


# In-memory chat history (swap for DB in production)
_history: dict[str, list[Message]] = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/query", response_model=Message)
async def query_document(req: QueryRequest):
    # Retrieve relevant chunks
    chunks = search(
        query=req.query, 
        session_id=req.session_id,
        doc_id=req.doc_id
    )
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant content found. Please upload a document first.",
        )

    # Build history for multi-turn context
    prior = _history.get(req.session_id, [])
    history_dicts = [m.model_dump() for m in prior]

    # Generate answer
    answer = generate_answer(
        query=req.query,
        context_chunks=chunks,
        history=history_dicts,
    )

    # Persist turn
    session_msgs = _history.setdefault(req.session_id, [])
    session_msgs.append(Message(role="user", content=req.query))
    session_msgs.append(Message(role="assistant", content=answer))

    return Message(role="assistant", content=answer)


@router.get("/{session_id}", response_model=list[Message])
async def get_history(session_id: str):
    return _history.get(session_id, [])


@router.delete("/{session_id}")
async def clear_history(session_id: str):
    _history.pop(session_id, None)
    return {"detail": "cleared", "session_id": session_id}
