"""
llm_service.py — Groq API integration for LLaMA 2 text generation.
"""
from __future__ import annotations

from groq import Groq

from config import settings

_client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = (
    "You are DocChat, a helpful AI assistant that answers questions "
    "strictly based on the document context provided. "
    "If the answer is not in the context, say so clearly. "
    "Keep answers concise and cite which part of the document you used."
)


def generate_answer(
    query: str,
    context_chunks: list[str],
    history: list[dict] | None = None,
) -> str:
    """
    Build a RAG prompt and call the Groq LLM.

    Args:
        query:          The user's natural-language question.
        context_chunks: Retrieved text chunks from ChromaDB.
        history:        Optional list of {"role": ..., "content": ...} dicts.

    Returns:
        The model's answer as a plain string.
    """
    context = "\n\n---\n\n".join(context_chunks)

    user_message = (
        f"Context from the document:\n\n{context}\n\n"
        f"Question: {query}"
    )

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-6:])  # keep last 3 turns (6 messages)

    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model=settings.groq_model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
    )

    return response.choices[0].message.content
