from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.ingestion.dedup import compute_source_hash
from src.ingestion.mime_detect import detect_mime_type
from src.ingestion.source_resolver import ResolvedSource, resolve_source


class PreparedSource(BaseModel):
    source: str
    source_kind: str
    source_uri: str
    local_path: str | None = None
    file_name: str
    file_type: str | None = None
    content_hash: str
    tenant_id: str | None = None
    knowledge_base_id: str | None = None
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


class IngestionService:
    def __init__(self, data_dir) -> None:
        self.data_dir = data_dir

    def prepare(
        self,
        source: str,
        *,
        tenant_id: str | None = None,
        knowledge_base_id: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> PreparedSource:
        resolved = resolve_source(source, self.data_dir)
        return self._to_prepared_source(
            resolved,
            tenant_id=tenant_id,
            knowledge_base_id=knowledge_base_id,
            extra_metadata=extra_metadata or {},
        )

    def _to_prepared_source(
        self,
        resolved: ResolvedSource,
        *,
        tenant_id: str | None,
        knowledge_base_id: str | None,
        extra_metadata: dict[str, Any],
    ) -> PreparedSource:
        return PreparedSource(
            source=resolved.original_source,
            source_kind=resolved.source_kind,
            source_uri=resolved.source_uri,
            local_path=str(resolved.local_path) if resolved.local_path else None,
            file_name=resolved.file_name,
            file_type=detect_mime_type(resolved.file_name),
            content_hash=compute_source_hash(resolved),
            tenant_id=tenant_id,
            knowledge_base_id=knowledge_base_id,
            extra_metadata=extra_metadata,
        )
