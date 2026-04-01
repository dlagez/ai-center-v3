from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import create_app


def test_index_search_and_rag(isolated_settings) -> None:
    settings = isolated_settings
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    sample_file = settings.data_dir / "policy.txt"
    sample_file.write_text(
        "Travel reimbursement standard: hotel up to 500 CNY per night.",
        encoding="utf-8",
    )

    with TestClient(create_app()) as client:
        index_response = client.post(
            "/documents/index",
            json={
                "source": "policy.txt",
                "tenant_id": "t1",
                "knowledge_base_id": "kb_finance",
            },
        )
        assert index_response.status_code == 200
        payload = index_response.json()

        job_response = client.get(f"/jobs/{payload['job_id']}")
        assert job_response.status_code == 200
        assert job_response.json()["status"] == "finished"

        search_response = client.post(
            "/search",
            json={
                "query": "travel reimbursement",
                "top_k": 3,
                "metadata_filter": {
                    "tenant_id": "t1",
                    "knowledge_base_id": "kb_finance",
                },
            },
        )
        assert search_response.status_code == 200
        assert len(search_response.json()["results"]) >= 1

        rag_response = client.post(
            "/rag/query",
            json={
                "query": "What is the travel reimbursement standard?",
                "top_k": 3,
                "metadata_filter": {
                    "tenant_id": "t1",
                    "knowledge_base_id": "kb_finance",
                },
            },
        )
        assert rag_response.status_code == 200
        rag_payload = rag_response.json()
        assert rag_payload["answer"] == "Mock answer for: What is the travel reimbursement standard?"
        assert len(rag_payload["citations"]) >= 1
