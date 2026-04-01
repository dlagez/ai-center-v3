from __future__ import annotations

from typing import Any

from qdrant_client.http import models as qdrant_models


def build_qdrant_filter(metadata_filter: dict[str, Any]) -> qdrant_models.Filter | None:
    if not metadata_filter:
        return None

    must: list[qdrant_models.FieldCondition] = []
    for key, value in metadata_filter.items():
        must.append(
            qdrant_models.FieldCondition(
                key=key,
                match=qdrant_models.MatchValue(value=value),
            )
        )
    return qdrant_models.Filter(must=must)
