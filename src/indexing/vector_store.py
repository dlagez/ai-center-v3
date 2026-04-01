from __future__ import annotations

from src.infra.qdrant import QdrantStore
from src.models.chunk import DocChunk


class VectorStoreGateway:
    def __init__(self, qdrant_store: QdrantStore) -> None:
        self.qdrant_store = qdrant_store

    def upsert_chunks(self, chunks: list[DocChunk], vectors: list[list[float]]) -> None:
        self.qdrant_store.upsert_chunks(chunks, vectors)

    def delete_document(self, document_id: str) -> None:
        self.qdrant_store.delete_document(document_id)
