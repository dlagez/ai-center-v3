from __future__ import annotations

from typing import Protocol, TypedDict

from langchain_core.documents import Document

from src.models.chunk import DocChunk


class ParsedOutput(TypedDict, total=False):
    doc_chunks: list[DocChunk]
    markdown: str
    text: str
    structured_json: dict
    documents: list[Document]


class BaseDocumentLoader(Protocol):
    def load(self, source: str) -> ParsedOutput:
        ...
