from __future__ import annotations

from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from src.models.chunk import DocChunk


class QdrantStore:
    def __init__(self, storage_path: Path, collection_name: str, vector_size: int) -> None:
        self._client = QdrantClient(path=str(storage_path))
        self.collection_name = collection_name
        self.vector_size = vector_size

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self.collection_name):
            collection_info = self._client.get_collection(self.collection_name)
            existing_size = self._get_vector_size(collection_info)
            if existing_size is not None and existing_size != self.vector_size:
                raise RuntimeError(
                    "Qdrant collection vector size mismatch. "
                    f"Collection `{self.collection_name}` uses {existing_size}, "
                    f"but settings require {self.vector_size}."
                )
            return

        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def _get_vector_size(self, collection_info: Any) -> int | None:
        vectors = collection_info.config.params.vectors
        size = getattr(vectors, "size", None)
        if isinstance(size, int):
            return size
        return None

    def upsert_chunks(self, chunks: list[DocChunk], vectors: list[list[float]]) -> None:
        self.ensure_collection()
        points = [
            qdrant_models.PointStruct(
                id=chunk.chunk_id,
                vector=vector,
                payload=chunk.to_payload(),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        if points:
            self._client.upsert(collection_name=self.collection_name, points=points)

    def delete_document(self, document_id: str) -> None:
        self.ensure_collection()
        self._client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="document_id",
                            match=qdrant_models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    def query(
        self,
        query_vector: list[float],
        limit: int,
        query_filter: qdrant_models.Filter | None = None,
    ) -> list[Any]:
        self.ensure_collection()
        response = self._client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
        )
        return response.points

    def close(self) -> None:
        self._client.close()
