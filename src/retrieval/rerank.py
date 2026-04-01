from __future__ import annotations

from src.schemas.search import SearchHit


class IdentityReranker:
    def rerank(self, results: list[SearchHit]) -> list[SearchHit]:
        return results
