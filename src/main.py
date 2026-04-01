from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.deps import get_app_settings, get_db, get_qdrant_store
from src.api.routers import documents, jobs, rag, search
from src.config.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_app_settings()
    
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        configure_logging(settings.debug)
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.qdrant_path.mkdir(parents=True, exist_ok=True)
        get_db().initialize()
        qdrant_store = get_qdrant_store()
        qdrant_store.ensure_collection()
        yield
        qdrant_store.close()

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(documents.router, prefix=settings.api_prefix)
    app.include_router(search.router, prefix=settings.api_prefix)
    app.include_router(rag.router, prefix=settings.api_prefix)
    app.include_router(jobs.router, prefix=settings.api_prefix)
    return app


app = create_app()
