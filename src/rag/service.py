from __future__ import annotations

from src.rag.answer_chain import AnswerChain
from src.schemas.rag import RAGRequest, RAGResponse
from src.retrieval.service import RetrievalService


class RAGService:
    def __init__(self, retrieval_service: RetrievalService, answer_chain: AnswerChain) -> None:
        self.retrieval_service = retrieval_service
        self.answer_chain = answer_chain

    def answer(self, request: RAGRequest) -> RAGResponse:
        retriever = self.retrieval_service.as_retriever(
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
        )
        documents = retriever.invoke(request.query)
        return self.answer_chain.generate(request.query, documents)
