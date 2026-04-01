from __future__ import annotations

from src.embeddings.base import EmbeddingService
from src.indexing.upsert import UpsertResult
from src.indexing.vector_store import VectorStoreGateway
from src.models.chunk import DocChunk


class IndexingService:
    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStoreGateway,
    ) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def index_document(self, document_id: str, chunks: list[DocChunk]) -> UpsertResult:
        vectors = self.embeddings.embed_documents([chunk.text for chunk in chunks])
        self.vector_store.upsert_chunks(chunks, vectors)
        return UpsertResult(document_id=document_id, chunk_count=len(chunks))
