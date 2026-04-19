"""
document_loader.py — Extract raw text from PDF, DOCX, and TXT files.
"""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from docx import Document


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def load_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def load_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="replace")


def load_document(file_path: str, mime_type: str) -> str:
    """Dispatch to the correct loader based on MIME type."""
    loaders = {
        "application/pdf": load_pdf,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": load_docx,
        "text/plain": load_txt,
    }
    loader = loaders.get(mime_type)
    if loader is None:
        raise ValueError(f"Unsupported MIME type: {mime_type}")
    return loader(file_path)
