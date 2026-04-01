from __future__ import annotations

from src.infra.litellm_client import LiteLLMClient


class LiteLLMEmbeddingService:
    def __init__(self, client: LiteLLMClient) -> None:
        self.client = client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.client.embed_texts(texts)

    def embed_query(self, query: str) -> list[float]:
        return self.client.embed_texts([query])[0]
