from __future__ import annotations

from functools import lru_cache

from src.config.settings import Settings, get_settings
from src.embeddings.factory import EmbeddingFactory
from src.infra.db import SQLiteDatabase
from src.infra.qdrant import QdrantStore
from src.indexing.service import IndexingService
from src.indexing.vector_store import VectorStoreGateway
from src.ingestion.service import IngestionService
from src.processing.loaders.docling_loader import DoclingDocumentLoader
from src.rag.answer_chain import AnswerChain
from src.rag.service import RAGService
from src.repositories.chunk_repo import ChunkRepository
from src.repositories.document_repo import DocumentRepository
from src.repositories.job_repo import JobRepository
from src.retrieval.rerank import IdentityReranker
from src.retrieval.service import RetrievalService
from src.workflows.ingestion_graph import IngestionWorkflow
from src.workflows.reindex_graph import ReindexWorkflow


@lru_cache(maxsize=1)
def get_db() -> SQLiteDatabase:
    db = SQLiteDatabase(get_settings().sqlite_path)
    db.initialize()
    return db


@lru_cache(maxsize=1)
def get_document_repo() -> DocumentRepository:
    return DocumentRepository(get_db())


@lru_cache(maxsize=1)
def get_chunk_repo() -> ChunkRepository:
    return ChunkRepository(get_db())


@lru_cache(maxsize=1)
def get_job_repo() -> JobRepository:
    return JobRepository(get_db())


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService(get_settings().data_dir)


@lru_cache(maxsize=1)
def get_loader() -> DoclingDocumentLoader:
    return DoclingDocumentLoader()


@lru_cache(maxsize=1)
def get_embedding_service():
    settings = get_settings()
    return EmbeddingFactory.create(settings.embedding_dimensions)


@lru_cache(maxsize=1)
def get_qdrant_store() -> QdrantStore:
    settings = get_settings()
    return QdrantStore(
        storage_path=settings.qdrant_path,
        collection_name=settings.qdrant_collection,
        vector_size=settings.embedding_dimensions,
    )


@lru_cache(maxsize=1)
def get_vector_store_gateway() -> VectorStoreGateway:
    return VectorStoreGateway(get_qdrant_store())


@lru_cache(maxsize=1)
def get_indexing_service() -> IndexingService:
    return IndexingService(get_embedding_service(), get_vector_store_gateway())


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        qdrant_store=get_qdrant_store(),
        embeddings=get_embedding_service(),
        reranker=IdentityReranker(),
    )


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService(get_retrieval_service(), AnswerChain())


@lru_cache(maxsize=1)
def get_ingestion_workflow() -> IngestionWorkflow:
    return IngestionWorkflow(
        document_repo=get_document_repo(),
        chunk_repo=get_chunk_repo(),
        job_repo=get_job_repo(),
        loader=get_loader(),
        indexing_service=get_indexing_service(),
    )


@lru_cache(maxsize=1)
def get_reindex_workflow() -> ReindexWorkflow:
    return ReindexWorkflow(
        document_repo=get_document_repo(),
        job_repo=get_job_repo(),
        ingestion_service=get_ingestion_service(),
        ingestion_workflow=get_ingestion_workflow(),
    )


def get_app_settings() -> Settings:
    return get_settings()
