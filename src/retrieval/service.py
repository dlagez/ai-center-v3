from __future__ import annotations

from langchain_core.documents import Document

from src.embeddings.service import DeterministicEmbeddingService
from src.infra.qdrant import QdrantStore
from src.retrieval.filters import build_qdrant_filter
from src.retrieval.query_plan import QueryPlan
from src.retrieval.rerank import IdentityReranker
from src.retrieval.retriever_factory import QdrantRetriever
from src.schemas.search import SearchHit


class RetrievalService:
    def __init__(
        self,
        qdrant_store: QdrantStore,
        embeddings: DeterministicEmbeddingService,
        reranker: IdentityReranker | None = None,
    ) -> None:
        self.qdrant_store = qdrant_store
        self.embeddings = embeddings
        self.reranker = reranker or IdentityReranker()

    def as_retriever(
        self,
        *,
        top_k: int,
        metadata_filter: dict,
    ) -> QdrantRetriever:
        return QdrantRetriever(
            service=self,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    def search_documents(
        self,
        *,
        query: str,
        top_k: int,
        metadata_filter: dict,
    ) -> list[Document]:
        hits = self.search(query=query, top_k=top_k, metadata_filter=metadata_filter)
        return [
            Document(page_content=hit.text, metadata=hit.metadata | {"chunk_id": hit.chunk_id})
            for hit in hits
        ]

    def search(
        self,
        *,
        query: str,
        top_k: int,
        metadata_filter: dict,
    ) -> list[SearchHit]:
        plan = QueryPlan(query=query, top_k=top_k, metadata_filter=metadata_filter)
        vector = self.embeddings.embed_query(plan.query)
        raw_results = self.qdrant_store.query(
            query_vector=vector,
            limit=plan.top_k,
            query_filter=build_qdrant_filter(plan.metadata_filter),
        )

        hits = [
            SearchHit(
                chunk_id=str(point.id),
                document_id=point.payload.get("document_id"),
                text=point.payload.get("text", ""),
                score=float(point.score),
                metadata=dict(point.payload),
            )
            for point in raw_results
        ]
        return self.reranker.rerank(hits)
