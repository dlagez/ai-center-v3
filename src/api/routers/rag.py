from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_rag_service
from src.rag.service import RAGService
from src.schemas.rag import RAGRequest, RAGResponse

router = APIRouter(tags=["rag"])


@router.post("/rag/query", response_model=RAGResponse)
def rag_query(
    request: RAGRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> RAGResponse:
    return rag_service.answer(request)
