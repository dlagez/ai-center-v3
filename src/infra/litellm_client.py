from __future__ import annotations

from litellm import completion, embedding


class LiteLLMClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        api_base: str | None,
        chat_model: str | None,
        embedding_model: str | None,
        embedding_dimensions: int,
        embedding_batch_size: int,
        timeout_seconds: int,
        chat_temperature: float,
        chat_max_tokens: int,
    ) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.embedding_batch_size = max(1, embedding_batch_size)
        self.timeout_seconds = timeout_seconds
        self.chat_temperature = chat_temperature
        self.chat_max_tokens = chat_max_tokens

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self.embedding_model:
            raise RuntimeError(
                "LITELLM_EMBEDDING_MODEL is required before indexing or search."
            )

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.embedding_batch_size):
            batch = texts[start : start + self.embedding_batch_size]
            response = embedding(
                model=self.embedding_model,
                input=batch,
                dimensions=self.embedding_dimensions,
                api_key=self.api_key,
                api_base=self.api_base,
                timeout=self.timeout_seconds,
            )

            for item in response.data:
                vector = [float(value) for value in item["embedding"]]
                if len(vector) != self.embedding_dimensions:
                    raise RuntimeError(
                        "Embedding dimension mismatch. "
                        f"Expected {self.embedding_dimensions}, got {len(vector)}."
                    )
                vectors.append(vector)

        return vectors

    def complete_text(self, messages: list[dict[str, str]]) -> str:
        if not self.chat_model:
            raise RuntimeError("LITELLM_CHAT_MODEL is required before RAG queries.")

        response = completion(
            model=self.chat_model,
            messages=messages,
            api_key=self.api_key,
            base_url=self.api_base,
            timeout=self.timeout_seconds,
            temperature=self.chat_temperature,
            max_tokens=self.chat_max_tokens,
        )
        return str(response.choices[0].message.content).strip()
