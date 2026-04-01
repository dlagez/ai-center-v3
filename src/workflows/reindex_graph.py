from __future__ import annotations

from src.ingestion.service import IngestionService
from src.models.job import JobStatus
from src.repositories.document_repo import DocumentRepository
from src.repositories.job_repo import JobRepository
from src.workflows.ingestion_graph import IngestionWorkflow


class ReindexWorkflow:
    def __init__(
        self,
        *,
        document_repo: DocumentRepository,
        job_repo: JobRepository,
        ingestion_service: IngestionService,
        ingestion_workflow: IngestionWorkflow,
    ) -> None:
        self.document_repo = document_repo
        self.job_repo = job_repo
        self.ingestion_service = ingestion_service
        self.ingestion_workflow = ingestion_workflow

    def run_reindex_job(self, job_id: str, document_id: str) -> None:
        document = self.document_repo.get(document_id)
        if document is None:
            self.job_repo.update_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Document not found: {document_id}",
            )
            return

        prepared = self.ingestion_service.prepare(
            document.source_uri,
            tenant_id=document.tenant_id,
            knowledge_base_id=document.knowledge_base_id,
            extra_metadata=document.extra_metadata,
        )
        self.ingestion_workflow.run_index_job(
            job_id=job_id,
            document_id=document_id,
            prepared_payload=prepared.model_dump(),
        )
