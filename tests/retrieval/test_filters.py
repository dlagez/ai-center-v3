from __future__ import annotations

from src.retrieval.filters import build_qdrant_filter


def test_build_qdrant_filter() -> None:
    qdrant_filter = build_qdrant_filter({"tenant_id": "t1"})
    assert qdrant_filter is not None
    assert len(qdrant_filter.must) == 1
