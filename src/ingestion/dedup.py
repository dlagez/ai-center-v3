from __future__ import annotations

from src.ingestion.source_resolver import ResolvedSource
from src.utils.hashing import sha256_file, sha256_text


def compute_source_hash(resolved_source: ResolvedSource) -> str:
    if resolved_source.local_path is not None:
        return sha256_file(resolved_source.local_path)
    return sha256_text(resolved_source.source_uri)
