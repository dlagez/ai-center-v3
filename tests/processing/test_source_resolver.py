from __future__ import annotations

from pathlib import Path

from src.ingestion.source_resolver import resolve_source


def test_resolve_local_source_under_data_dir(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sample_file = data_dir / "a.txt"
    sample_file.write_text("hi", encoding="utf-8")

    resolved = resolve_source("a.txt", data_dir)

    assert resolved.source_kind == "local"
    assert resolved.local_path == sample_file.resolve()
