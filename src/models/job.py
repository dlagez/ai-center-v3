from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    FINISHED = "finished"


class JobRecord(BaseModel):
    id: str
    job_type: str
    document_id: str | None = None
    source: str | None = None
    status: JobStatus
    error_message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str
