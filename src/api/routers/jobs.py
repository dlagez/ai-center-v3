from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_job_repo
from src.repositories.job_repo import JobRepository
from src.schemas.job import JobResponse

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    job_repo: JobRepository = Depends(get_job_repo),
) -> JobResponse:
    job = job_repo.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    payload = job.model_dump()
    payload["status"] = job.status.value
    return JobResponse.model_validate(payload)
