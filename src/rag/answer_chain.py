from __future__ import annotations

from langchain_core.documents import Document

from src.rag.prompt_builder import build_context_prompt
from src.schemas.rag import Citation, RAGResponse


class AnswerChain:
    def generate(self, query: str, documents: list[Document]) -> RAGResponse:
        if not documents:
            return RAGResponse(answer="未检索到相关内容。", citations=[])

        prompt = build_context_prompt(query, documents)
        citations: list[Citation] = []
        answer_lines = ["根据检索结果，相关内容如下："]
        for index, document in enumerate(documents[:3], start=1):
            metadata = dict(document.metadata)
            citations.append(
                Citation(
                    chunk_id=str(metadata.get("chunk_id", "")),
                    document_id=metadata.get("document_id"),
                    page=metadata.get("page"),
                    section_title=metadata.get("section_title"),
                    score=metadata.get("score"),
                )
            )
            answer_lines.append(f"{index}. {document.page_content[:240]}")
        answer_lines.append("")
        answer_lines.append("调试提示：")
        answer_lines.append(prompt[:400])
        return RAGResponse(answer="\n".join(answer_lines), citations=citations)
