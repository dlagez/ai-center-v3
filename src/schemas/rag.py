from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    query: str
    top_k: int = 5
    metadata_filter: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    chunk_id: str
    document_id: str | None = None
    page: int | None = None
    section_title: str | None = None
    score: float | None = None


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
