from __future__ import annotations

import pytest

from src.api import deps
from src.config.settings import get_settings
from src.infra.litellm_client import LiteLLMClient


def _clear_caches() -> None:
    get_settings.cache_clear()
    deps.get_db.cache_clear()
    deps.get_document_repo.cache_clear()
    deps.get_chunk_repo.cache_clear()
    deps.get_job_repo.cache_clear()
    deps.get_ingestion_service.cache_clear()
    deps.get_loader.cache_clear()
    deps.get_litellm_client.cache_clear()
    deps.get_embedding_service.cache_clear()
    if deps.get_qdrant_store.cache_info().currsize:
        deps.get_qdrant_store().close()
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

    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("SQLITE_PATH", str(sqlite_path))
    monkeypatch.setenv("QDRANT_PATH", str(qdrant_path))
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "8")
    monkeypatch.setenv("LITELLM_CHAT_MODEL", "mock-chat")
    monkeypatch.setenv("LITELLM_EMBEDDING_MODEL", "mock-embedding")

    _clear_caches()
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield settings
    _clear_caches()


@pytest.fixture(autouse=True)
def mock_litellm(monkeypatch):
    def fake_embed_texts(self: LiteLLMClient, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            base = float((sum(ord(char) for char in text) % 17) + 1)
            vector = [base + index for index in range(self.embedding_dimensions)]
            vectors.append(vector)
        return vectors

    def fake_complete_text(self: LiteLLMClient, messages: list[dict[str, str]]) -> str:
        question = messages[-1]["content"].split("Question:\n", maxsplit=1)[-1]
        question = question.split("\n\nRetrieved context:\n", maxsplit=1)[0].strip()
        return f"Mock answer for: {question}"

    monkeypatch.setattr(LiteLLMClient, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(LiteLLMClient, "complete_text", fake_complete_text)
