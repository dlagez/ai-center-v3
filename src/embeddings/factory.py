from __future__ import annotations

from src.embeddings.service import DeterministicEmbeddingService


class EmbeddingFactory:
    @staticmethod
    def create(dimensions: int) -> DeterministicEmbeddingService:
        return DeterministicEmbeddingService(dimensions=dimensions)
