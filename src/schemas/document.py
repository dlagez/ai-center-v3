from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentParseRequest(BaseModel):
    source: str
    tenant_id: str | None = None
    knowledge_base_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentReindexRequest(BaseModel):
    document_id: str


class DocumentAcceptedResponse(BaseModel):
    job_id: str
    document_id: str
    status: str


class DocumentResponse(BaseModel):
    id: str
    source_uri: str
    source_kind: str
    file_name: str
    file_type: str | None = None
    parser: str
    status: str
    tenant_id: str | None = None
    knowledge_base_id: str | None = None
    chunk_count: int
    indexed_at: str | None = None
    created_at: str
    updated_at: str
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
