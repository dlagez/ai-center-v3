from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from src.config.constants import (
    API_PREFIX,
    APP_NAME,
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_LITELLM_CHAT_MAX_TOKENS,
    DEFAULT_LITELLM_CHAT_TEMPERATURE,
    DEFAULT_LITELLM_EMBEDDING_BATCH_SIZE,
    DEFAULT_LITELLM_TIMEOUT_SECONDS,
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
    litellm_api_key: str | None
    litellm_api_base: str | None
    litellm_chat_model: str | None
    litellm_embedding_model: str | None
    litellm_timeout_seconds: int
    litellm_chat_temperature: float
    litellm_chat_max_tokens: int
    litellm_embedding_batch_size: int
    debug: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = Path(os.getenv("DATA_DIR", str(base_dir / "data"))).resolve()
    sqlite_path = Path(
        os.getenv("SQLITE_PATH", str(data_dir / "document_processing.sqlite3"))
    ).resolve()
    qdrant_path = Path(os.getenv("QDRANT_PATH", str(data_dir / ".qdrant"))).resolve()

    return Settings(
        app_name=os.getenv("APP_NAME", APP_NAME),
        api_prefix=os.getenv("API_PREFIX", API_PREFIX),
        base_dir=base_dir,
        data_dir=data_dir,
        sqlite_path=sqlite_path,
        qdrant_path=qdrant_path,
        qdrant_collection=os.getenv("QDRANT_COLLECTION", DEFAULT_QDRANT_COLLECTION),
        embedding_dimensions=int(
            os.getenv("EMBEDDING_DIMENSIONS", DEFAULT_EMBEDDING_DIMENSIONS)
        ),
        default_top_k=int(os.getenv("DEFAULT_TOP_K", DEFAULT_TOP_K)),
        litellm_api_key=os.getenv("LITELLM_API_KEY") or None,
        litellm_api_base=os.getenv("LITELLM_API_BASE") or None,
        litellm_chat_model=os.getenv("LITELLM_CHAT_MODEL") or None,
        litellm_embedding_model=os.getenv("LITELLM_EMBEDDING_MODEL") or None,
        litellm_timeout_seconds=int(
            os.getenv("LITELLM_TIMEOUT_SECONDS", DEFAULT_LITELLM_TIMEOUT_SECONDS)
        ),
        litellm_chat_temperature=float(
            os.getenv("LITELLM_CHAT_TEMPERATURE", DEFAULT_LITELLM_CHAT_TEMPERATURE)
        ),
        litellm_chat_max_tokens=int(
            os.getenv("LITELLM_CHAT_MAX_TOKENS", DEFAULT_LITELLM_CHAT_MAX_TOKENS)
        ),
        litellm_embedding_batch_size=int(
            os.getenv(
                "LITELLM_EMBEDDING_BATCH_SIZE",
                DEFAULT_LITELLM_EMBEDDING_BATCH_SIZE,
            )
        ),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
