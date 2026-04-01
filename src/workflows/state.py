from __future__ import annotations

from pydantic import BaseModel

from src.models.job import JobStatus


class WorkflowState(BaseModel):
    job_id: str
    document_id: str
    status: JobStatus
