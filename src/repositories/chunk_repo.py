from __future__ import annotations

from src.infra.db import SQLiteDatabase, dumps_json, loads_json
from src.models.chunk import DocChunk


class ChunkRepository:
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def replace_for_document(self, document_id: str, chunks: list[DocChunk]) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            conn.executemany(
                """
                INSERT INTO chunks (
                    chunk_id, document_id, text, source_uri, file_name, file_type, page,
                    section_title, parser, tenant_id, knowledge_base_id, chunk_type,
                    chunk_index, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        document_id,
                        chunk.text,
                        chunk.source_uri,
                        chunk.file_name,
                        chunk.file_type,
                        chunk.page,
                        chunk.section_title,
                        chunk.parser,
                        chunk.tenant_id,
                        chunk.knowledge_base_id,
                        chunk.chunk_type,
                        chunk.chunk_index,
                        dumps_json(chunk.metadata),
                    )
                    for chunk in chunks
                ],
            )

    def list_by_document(self, document_id: str) -> list[DocChunk]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index",
                (document_id,),
            ).fetchall()
        items: list[DocChunk] = []
        for row in rows:
            payload = dict(row)
            payload["metadata"] = loads_json(payload.pop("metadata"))
            items.append(DocChunk.model_validate(payload))
        return items

    def count_by_document(self, document_id: str) -> int:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM chunks WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return int(row["count"])
