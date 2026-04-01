from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field


class QdrantRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: Any
    metadata_filter: dict[str, Any] = Field(default_factory=dict)
    top_k: int = 5

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        return self.service.search_documents(
            query=query,
            top_k=self.top_k,
            metadata_filter=self.metadata_filter,
        )
