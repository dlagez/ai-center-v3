from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class SQLiteDatabase:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    source_uri TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    parser TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    tenant_id TEXT,
                    knowledge_base_id TEXT,
                    status TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    indexed_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    extra_metadata TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source_uri TEXT,
                    file_name TEXT,
                    file_type TEXT,
                    page INTEGER,
                    section_title TEXT,
                    parser TEXT NOT NULL,
                    tenant_id TEXT,
                    knowledge_base_id TEXT,
                    chunk_type TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    document_id TEXT,
                    source TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS knowledge_bases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tenant_id TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash);
                CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_document_id ON jobs(document_id);
                """
            )

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


def dumps_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def loads_json(value: str | None) -> dict:
    if not value:
        return {}
    return json.loads(value)
