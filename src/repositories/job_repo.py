from __future__ import annotations

from src.infra.db import SQLiteDatabase, dumps_json, loads_json
from src.models.job import JobRecord, JobStatus


class JobRepository:
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def create(self, job: JobRecord) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, job_type, document_id, source, status, error_message,
                    payload, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.job_type,
                    job.document_id,
                    job.source,
                    job.status.value,
                    job.error_message,
                    dumps_json(job.payload),
                    job.created_at,
                    job.updated_at,
                ),
            )

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error_message: str | None = None,
    ) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, error_message = COALESCE(?, error_message), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status.value, error_message, job_id),
            )

    def update(self, job: JobRecord) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, error_message = ?, payload = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    job.status.value,
                    job.error_message,
                    dumps_json(job.payload),
                    job.updated_at,
                    job.id,
                ),
            )

    def get(self, job_id: str) -> JobRecord | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["payload"] = loads_json(payload.pop("payload"))
        payload["status"] = JobStatus(payload["status"])
        return JobRecord.model_validate(payload)
