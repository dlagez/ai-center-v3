from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from src.config.constants import (
    API_PREFIX,
    APP_NAME,
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_QDRANT_COLLECTION,
    DEFAULT_TOP_K,
)


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_name: str
    api_prefix: str
    base_dir: Path
    data_dir: Path
    sqlite_path: Path
    qdrant_path: Path
    qdrant_collection: str
    embedding_dimensions: int
    default_top_k: int
    debug: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = Path(os.getenv("AI_CENTER_DATA_DIR", str(base_dir / "data"))).resolve()
    sqlite_path = Path(
        os.getenv("AI_CENTER_SQLITE_PATH", str(data_dir / "document_processing.sqlite3"))
    ).resolve()
    qdrant_path = Path(
        os.getenv("AI_CENTER_QDRANT_PATH", str(data_dir / ".qdrant"))
    ).resolve()

    return Settings(
        app_name=os.getenv("AI_CENTER_APP_NAME", APP_NAME),
        api_prefix=os.getenv("AI_CENTER_API_PREFIX", API_PREFIX),
        base_dir=base_dir,
        data_dir=data_dir,
        sqlite_path=sqlite_path,
        qdrant_path=qdrant_path,
        qdrant_collection=os.getenv(
            "AI_CENTER_QDRANT_COLLECTION", DEFAULT_QDRANT_COLLECTION
        ),
        embedding_dimensions=int(
            os.getenv("AI_CENTER_EMBEDDING_DIMENSIONS", DEFAULT_EMBEDDING_DIMENSIONS)
        ),
        default_top_k=int(os.getenv("AI_CENTER_DEFAULT_TOP_K", DEFAULT_TOP_K)),
        debug=os.getenv("AI_CENTER_DEBUG", "false").lower() == "true",
    )
