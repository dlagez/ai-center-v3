from __future__ import annotations

from langchain_core.documents import Document


def build_context_prompt(query: str, documents: list[Document]) -> str:
    context_blocks = []
    for index, document in enumerate(documents, start=1):
        context_blocks.append(f"[{index}] {document.page_content}")
    context = "\n\n".join(context_blocks)
    return f"问题：{query}\n\n检索上下文：\n{context}"
