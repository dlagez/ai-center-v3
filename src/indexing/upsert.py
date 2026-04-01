from __future__ import annotations

from pydantic import BaseModel


class UpsertResult(BaseModel):
    document_id: str
    chunk_count: int
