from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_retrieval_service
from src.retrieval.service import RetrievalService
from src.schemas.search import SearchRequest, SearchResponse

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse:
    results = retrieval_service.search(
        query=request.query,
        top_k=request.top_k,
        metadata_filter=request.metadata_filter,
    )
    return SearchResponse(results=results)
