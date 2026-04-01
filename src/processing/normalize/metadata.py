from __future__ import annotations

from src.ingestion.service import PreparedSource
from src.models.chunk import DocChunk
from src.utils.ids import new_id


def normalize_doc_chunks(
    chunks: list[DocChunk],
    prepared_source: PreparedSource,
    *,
    document_id: str,
    parser: str = "docling",
) -> list[DocChunk]:
    normalized: list[DocChunk] = []
    for index, chunk in enumerate(chunks):
        metadata = dict(chunk.metadata)
        metadata.setdefault("source", prepared_source.source_uri)
        normalized.append(
            chunk.model_copy(
                update={
                    "chunk_id": chunk.chunk_id or new_id("chunk"),
                    "document_id": document_id,
                    "source_uri": prepared_source.source_uri,
                    "file_name": prepared_source.file_name,
                    "file_type": prepared_source.file_type,
                    "parser": parser,
                    "tenant_id": prepared_source.tenant_id,
                    "knowledge_base_id": prepared_source.knowledge_base_id,
                    "chunk_index": index,
                    "metadata": metadata,
                }
            )
        )
    return normalized
