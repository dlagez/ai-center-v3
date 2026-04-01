from __future__ import annotations

import json
from pathlib import Path
from urllib.request import urlopen

from langchain_core.documents import Document

from src.models.chunk import DocChunk
from src.processing.loaders.base import ParsedOutput


class DoclingDocumentLoader:
    def load(self, source: str) -> ParsedOutput:
        try:
            return self._load_with_docling(source)
        except ModuleNotFoundError:
            return self._load_with_text_fallback(source)

    def _load_with_docling(self, source: str) -> ParsedOutput:
        from langchain_docling import DoclingLoader
        from langchain_docling.loader import ExportType

        loader = DoclingLoader(source, export_type=ExportType.DOC_CHUNKS)
        documents = loader.load()
        return {
            "documents": documents,
            "doc_chunks": [
                self._document_to_chunk(index, document)
                for index, document in enumerate(documents)
            ],
        }

    def _load_with_text_fallback(self, source: str) -> ParsedOutput:
        text = self._read_text(source)
        chunk = DocChunk(
            chunk_id="",
            text=text.strip(),
            chunk_index=0,
            metadata={"fallback_loader": True},
        )
        return {
            "text": text,
            "documents": [Document(page_content=text, metadata={"fallback_loader": True})],
            "doc_chunks": [chunk],
        }

    def _document_to_chunk(self, index: int, document: Document) -> DocChunk:
        metadata = dict(document.metadata)
        page = metadata.get("page")
        if isinstance(page, str) and page.isdigit():
            page = int(page)

        return DocChunk(
            chunk_id="",
            text=document.page_content,
            page=page if isinstance(page, int) else None,
            section_title=metadata.get("section_title") or metadata.get("title"),
            chunk_type=str(metadata.get("chunk_type", "text")),
            chunk_index=index,
            metadata=metadata,
        )

    def _read_text(self, source: str) -> str:
        if source.startswith(("http://", "https://")):
            with urlopen(source) as response:  # noqa: S310
                return response.read().decode("utf-8")

        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as handle:
                return json.dumps(json.load(handle), ensure_ascii=False, indent=2)
        with path.open("r", encoding="utf-8") as handle:
            return handle.read()
