from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from src.infra.litellm_client import LiteLLMClient
from src.rag.prompt_builder import build_answer_messages
from src.schemas.rag import Citation, RAGResponse


class AnswerChain:
    def __init__(self, client: LiteLLMClient) -> None:
        self.client = client

    def generate(self, query: str, documents: list[Document]) -> RAGResponse:
        citations = [self._build_citation(document) for document in documents[:5]]
        if not documents:
            return RAGResponse(answer="No relevant context was retrieved.", citations=[])

        answer = self.client.complete_text(build_answer_messages(query, documents))
        if not answer:
            answer = "The model returned an empty answer."
        return RAGResponse(answer=answer, citations=citations)

    def _build_citation(self, document: Document) -> Citation:
        metadata = dict(document.metadata)
        return Citation(
            chunk_id=str(metadata.get("chunk_id", "")),
            document_id=self._to_optional_str(metadata.get("document_id")),
            page=self._to_optional_int(metadata.get("page")),
            section_title=self._to_optional_str(metadata.get("section_title")),
            score=self._to_optional_float(metadata.get("score")),
        )

    def _to_optional_str(self, value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    def _to_optional_int(self, value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    def _to_optional_float(self, value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
