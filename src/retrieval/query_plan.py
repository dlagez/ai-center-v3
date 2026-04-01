from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    query: str
    top_k: int
    metadata_filter: dict[str, Any] = Field(default_factory=dict)
