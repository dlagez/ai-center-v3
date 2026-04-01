from __future__ import annotations

from src.models.chunk import DocChunk


def validate_doc_chunks(chunks: list[DocChunk]) -> list[DocChunk]:
    valid_chunks: list[DocChunk] = []
    for chunk in chunks:
        if not chunk.text.strip():
            continue
        valid_chunks.append(chunk)
    if not valid_chunks:
        raise ValueError("No valid DOC_CHUNKS were produced.")
    return valid_chunks
