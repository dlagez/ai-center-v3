from __future__ import annotations

from langchain_core.documents import Document

SYSTEM_PROMPT = (
    "You answer questions using only the retrieved context. "
    "Be concise, do not invent facts, and say when the context is insufficient."
)


def build_answer_messages(query: str, documents: list[Document]) -> list[dict[str, str]]:
    context_blocks: list[str] = []
    for index, document in enumerate(documents, start=1):
        metadata = dict(document.metadata)
        tags: list[str] = []
        if metadata.get("file_name"):
            tags.append(f"file={metadata['file_name']}")
        if metadata.get("page") is not None:
            tags.append(f"page={metadata['page']}")
        if metadata.get("section_title"):
            tags.append(f"section={metadata['section_title']}")

        header = f"[{index}]"
        if tags:
            header = f"{header} ({', '.join(tags)})"
        context_blocks.append(f"{header}\n{document.page_content}")

    context = "\n\n".join(context_blocks)
    user_prompt = (
        "Answer the question with the retrieved context below. "
        "If the context is insufficient, say so clearly. "
        "Prefer the same language as the question.\n\n"
        f"Question:\n{query}\n\n"
        f"Retrieved context:\n{context}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
