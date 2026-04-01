from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocChunk(BaseModel):
    chunk_id: str
    document_id: str | None = None
    text: str
    source_uri: str | None = None
    file_name: str | None = None
    file_type: str | None = None
    page: int | None = None
    section_title: str | None = None
    parser: str = "docling"
    tenant_id: str | None = None
    knowledge_base_id: str | None = None
    chunk_type: str = "text"
    chunk_index: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "source_uri": self.source_uri,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "page": self.page,
            "section_title": self.section_title,
            "parser": self.parser,
            "tenant_id": self.tenant_id,
            "knowledge_base_id": self.knowledge_base_id,
            "chunk_type": self.chunk_type,
            "chunk_index": self.chunk_index,
        }
        payload.update(self.metadata)
        return payload
