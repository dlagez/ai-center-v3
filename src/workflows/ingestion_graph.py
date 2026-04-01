from __future__ import annotations

from src.ingestion.service import PreparedSource
from src.models.chunk import DocChunk
from src.models.document import DocumentRecord
from src.models.job import JobStatus
from src.processing.loaders.base import BaseDocumentLoader
from src.processing.normalize.metadata import normalize_doc_chunks
from src.processing.normalize.validators import validate_doc_chunks
from src.repositories.chunk_repo import ChunkRepository
from src.repositories.document_repo import DocumentRepository
from src.repositories.job_repo import JobRepository
from src.indexing.service import IndexingService
from src.utils.time import utc_now_iso


class IngestionWorkflow:
    def __init__(
        self,
        *,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        job_repo: JobRepository,
        loader: BaseDocumentLoader,
        indexing_service: IndexingService,
    ) -> None:
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.job_repo = job_repo
        self.loader = loader
        self.indexing_service = indexing_service

    def run_parse_job(self, job_id: str, document_id: str, prepared_payload: dict) -> None:
        prepared = PreparedSource.model_validate(prepared_payload)
        self.job_repo.update_status(job_id, JobStatus.RUNNING)
        try:
            chunks = self._parse_doc_chunks(prepared, document_id)
            self.chunk_repo.replace_for_document(document_id, chunks)
            self._update_document(
                document_id,
                status="parsed",
                chunk_count=len(chunks),
            )
            self.job_repo.update_status(job_id, JobStatus.FINISHED)
        except Exception as exc:
            self._mark_failed(job_id, document_id, exc)

    def run_index_job(self, job_id: str, document_id: str, prepared_payload: dict) -> None:
        prepared = PreparedSource.model_validate(prepared_payload)
        self.job_repo.update_status(job_id, JobStatus.RUNNING)
        try:
            chunks = self._parse_doc_chunks(prepared, document_id)
            self.chunk_repo.replace_for_document(document_id, chunks)
            self.indexing_service.index_document(document_id, chunks)
            self._update_document(
                document_id,
                status="indexed",
                chunk_count=len(chunks),
                indexed_at=utc_now_iso(),
            )
            self.job_repo.update_status(job_id, JobStatus.FINISHED)
        except Exception as exc:
            self._mark_failed(job_id, document_id, exc)

    def _parse_doc_chunks(self, prepared: PreparedSource, document_id: str) -> list[DocChunk]:
        source = prepared.local_path or prepared.source_uri
        parsed = self.loader.load(source)
        raw_chunks = parsed.get("doc_chunks", [])
        normalized = normalize_doc_chunks(raw_chunks, prepared, document_id=document_id)
        return validate_doc_chunks(normalized)

    def _update_document(
        self,
        document_id: str,
        *,
        status: str,
        chunk_count: int,
        indexed_at: str | None = None,
    ) -> None:
        existing = self.document_repo.get(document_id)
        if existing is None:
            return
        self.document_repo.upsert(
            existing.model_copy(
                update={
                    "status": status,
                    "chunk_count": chunk_count,
                    "indexed_at": indexed_at or existing.indexed_at,
                    "updated_at": utc_now_iso(),
                }
            )
        )

    def _mark_failed(self, job_id: str, document_id: str, exc: Exception) -> None:
        existing = self.document_repo.get(document_id)
        if existing is not None:
            self.document_repo.upsert(
                existing.model_copy(
                    update={"status": "failed", "updated_at": utc_now_iso()}
                )
            )
        self.job_repo.update_status(job_id, JobStatus.FAILED, error_message=str(exc))
