"""
chunking.py — Split raw text into overlapping chunks for the RAG pipeline.
"""
from __future__ import annotations

from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import settings


def chunk_text(text: str) -> list[str]:
    """
    Split *text* into overlapping chunks using LangChain's
    RecursiveCharacterTextSplitter.  Chunk size and overlap are
    read from settings (backed by .env).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)
