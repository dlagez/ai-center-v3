from __future__ import annotations

import math


class DeterministicEmbeddingService:
    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for index, char in enumerate(query):
            bucket = index % self.dimensions
            vector[bucket] += (ord(char) % 97) / 97.0

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
