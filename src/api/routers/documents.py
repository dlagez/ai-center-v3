from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from src.api.deps import (
    get_document_repo,
    get_ingestion_service,
    get_ingestion_workflow,
    get_job_repo,
    get_reindex_workflow,
)
from src.models.document import DocumentRecord
from src.models.job import JobRecord, JobStatus
from src.repositories.document_repo import DocumentRepository
from src.repositories.job_repo import JobRepository
from src.schemas.document import (
    DocumentAcceptedResponse,
    DocumentParseRequest,
    DocumentReindexRequest,
    DocumentResponse,
)
from src.utils.ids import new_id
from src.utils.time import utc_now_iso

router = APIRouter(tags=["documents"])


@router.post("/documents/parse", response_model=DocumentAcceptedResponse)
def parse_document(
    request: DocumentParseRequest,
    background_tasks: BackgroundTasks,
    ingestion_service=Depends(get_ingestion_service),
    workflow=Depends(get_ingestion_workflow),
    document_repo: DocumentRepository = Depends(get_document_repo),
    job_repo: JobRepository = Depends(get_job_repo),
) -> DocumentAcceptedResponse:
    prepared = ingestion_service.prepare(
        request.source,
        tenant_id=request.tenant_id,
        knowledge_base_id=request.knowledge_base_id,
        extra_metadata=request.metadata,
    )
    now = utc_now_iso()
    document_id = new_id("doc")
    job_id = new_id("job")

    document_repo.upsert(
        DocumentRecord(
            id=document_id,
            source_uri=prepared.source_uri,
            source_kind=prepared.source_kind,
            file_name=prepared.file_name,
            file_type=prepared.file_type,
            parser="docling",
            content_hash=prepared.content_hash,
            tenant_id=prepared.tenant_id,
            knowledge_base_id=prepared.knowledge_base_id,
            status=JobStatus.QUEUED.value,
            created_at=now,
            updated_at=now,
            extra_metadata=prepared.extra_metadata,
        )
    )
    job_repo.create(
        JobRecord(
            id=job_id,
            job_type="parse",
            document_id=document_id,
            source=request.source,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
    )
    background_tasks.add_task(
        workflow.run_parse_job,
        job_id,
        document_id,
        prepared.model_dump(),
    )
    return DocumentAcceptedResponse(
        job_id=job_id,
        document_id=document_id,
        status=JobStatus.QUEUED.value,
    )


@router.post("/documents/index", response_model=DocumentAcceptedResponse)
def index_document(
    request: DocumentParseRequest,
    background_tasks: BackgroundTasks,
    ingestion_service=Depends(get_ingestion_service),
    workflow=Depends(get_ingestion_workflow),
    document_repo: DocumentRepository = Depends(get_document_repo),
    job_repo: JobRepository = Depends(get_job_repo),
) -> DocumentAcceptedResponse:
    prepared = ingestion_service.prepare(
        request.source,
        tenant_id=request.tenant_id,
        knowledge_base_id=request.knowledge_base_id,
        extra_metadata=request.metadata,
    )
    now = utc_now_iso()
    document_id = new_id("doc")
    job_id = new_id("job")

    document_repo.upsert(
        DocumentRecord(
            id=document_id,
            source_uri=prepared.source_uri,
            source_kind=prepared.source_kind,
            file_name=prepared.file_name,
            file_type=prepared.file_type,
            parser="docling",
            content_hash=prepared.content_hash,
            tenant_id=prepared.tenant_id,
            knowledge_base_id=prepared.knowledge_base_id,
            status=JobStatus.QUEUED.value,
            created_at=now,
            updated_at=now,
            extra_metadata=prepared.extra_metadata,
        )
    )
    job_repo.create(
        JobRecord(
            id=job_id,
            job_type="index",
            document_id=document_id,
            source=request.source,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
    )
    background_tasks.add_task(
        workflow.run_index_job,
        job_id,
        document_id,
        prepared.model_dump(),
    )
    return DocumentAcceptedResponse(
        job_id=job_id,
        document_id=document_id,
        status=JobStatus.QUEUED.value,
    )


@router.post("/documents/reindex", response_model=DocumentAcceptedResponse)
def reindex_document(
    request: DocumentReindexRequest,
    background_tasks: BackgroundTasks,
    workflow=Depends(get_reindex_workflow),
    job_repo: JobRepository = Depends(get_job_repo),
) -> DocumentAcceptedResponse:
    now = utc_now_iso()
    job_id = new_id("job")
    job_repo.create(
        JobRecord(
            id=job_id,
            job_type="reindex",
            document_id=request.document_id,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
    )
    background_tasks.add_task(workflow.run_reindex_job, job_id, request.document_id)
    return DocumentAcceptedResponse(
        job_id=job_id,
        document_id=request.document_id,
        status=JobStatus.QUEUED.value,
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentResponse:
    document = document_repo.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document.model_dump())
