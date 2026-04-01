from __future__ import annotations

import pytest

from src.api import deps
from src.config.settings import get_settings


def _clear_caches() -> None:
    get_settings.cache_clear()
    deps.get_db.cache_clear()
    deps.get_document_repo.cache_clear()
    deps.get_chunk_repo.cache_clear()
    deps.get_job_repo.cache_clear()
    deps.get_ingestion_service.cache_clear()
    deps.get_loader.cache_clear()
    deps.get_embedding_service.cache_clear()
    deps.get_qdrant_store.cache_clear()
    deps.get_vector_store_gateway.cache_clear()
    deps.get_indexing_service.cache_clear()
    deps.get_retrieval_service.cache_clear()
    deps.get_rag_service.cache_clear()
    deps.get_ingestion_workflow.cache_clear()
    deps.get_reindex_workflow.cache_clear()


@pytest.fixture()
def isolated_settings(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    sqlite_path = tmp_path / "document_processing.sqlite3"
    qdrant_path = tmp_path / ".qdrant"

    monkeypatch.setenv("AI_CENTER_DATA_DIR", str(data_dir))
    monkeypatch.setenv("AI_CENTER_SQLITE_PATH", str(sqlite_path))
    monkeypatch.setenv("AI_CENTER_QDRANT_PATH", str(qdrant_path))

    _clear_caches()
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield settings
    _clear_caches()
