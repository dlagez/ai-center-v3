from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentRecord(BaseModel):
    id: str
    source_uri: str
    source_kind: str
    file_name: str
    file_type: str | None = None
    parser: str = "docling"
    content_hash: str
    tenant_id: str | None = None
    knowledge_base_id: str | None = None
    status: str
    chunk_count: int = 0
    indexed_at: str | None = None
    created_at: str
    updated_at: str
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
