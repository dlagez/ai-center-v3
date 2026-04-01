from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel


class ResolvedSource(BaseModel):
    original_source: str
    source_kind: str
    source_uri: str
    local_path: Path | None = None
    file_name: str


def is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"}


def resolve_source(source: str, data_dir: Path) -> ResolvedSource:
    if is_url(source):
        parsed = urlparse(source)
        file_name = Path(parsed.path).name or "remote-document"
        return ResolvedSource(
            original_source=source,
            source_kind="url",
            source_uri=source,
            file_name=file_name,
        )

    local_path = Path(source)
    if not local_path.is_absolute():
        local_path = (data_dir / local_path).resolve()
    else:
        local_path = local_path.resolve()

    data_root = data_dir.resolve()
    if data_root not in local_path.parents and local_path != data_root:
        raise ValueError(f"Local source must stay under data dir: {data_root}")
    if not local_path.exists() or not local_path.is_file():
        raise FileNotFoundError(f"Source file not found: {local_path}")

    return ResolvedSource(
        original_source=source,
        source_kind="local",
        source_uri=str(local_path),
        local_path=local_path,
        file_name=local_path.name,
    )
