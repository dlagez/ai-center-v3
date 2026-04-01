from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    metadata_filter: dict[str, Any] = Field(default_factory=dict)


class SearchHit(BaseModel):
    chunk_id: str
    document_id: str | None = None
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    results: list[SearchHit]
