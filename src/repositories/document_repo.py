from __future__ import annotations

from src.infra.db import SQLiteDatabase, dumps_json, loads_json
from src.models.document import DocumentRecord


class DocumentRepository:
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def upsert(self, document: DocumentRecord) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, source_uri, source_kind, file_name, file_type, parser, content_hash,
                    tenant_id, knowledge_base_id, status, chunk_count, indexed_at,
                    created_at, updated_at, extra_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_uri=excluded.source_uri,
                    source_kind=excluded.source_kind,
                    file_name=excluded.file_name,
                    file_type=excluded.file_type,
                    parser=excluded.parser,
                    content_hash=excluded.content_hash,
                    tenant_id=excluded.tenant_id,
                    knowledge_base_id=excluded.knowledge_base_id,
                    status=excluded.status,
                    chunk_count=excluded.chunk_count,
                    indexed_at=excluded.indexed_at,
                    updated_at=excluded.updated_at,
                    extra_metadata=excluded.extra_metadata
                """,
                (
                    document.id,
                    document.source_uri,
                    document.source_kind,
                    document.file_name,
                    document.file_type,
                    document.parser,
                    document.content_hash,
                    document.tenant_id,
                    document.knowledge_base_id,
                    document.status,
                    document.chunk_count,
                    document.indexed_at,
                    document.created_at,
                    document.updated_at,
                    dumps_json(document.extra_metadata),
                ),
            )

    def get(self, document_id: str) -> DocumentRecord | None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["extra_metadata"] = loads_json(payload.pop("extra_metadata"))
        return DocumentRecord.model_validate(payload)
