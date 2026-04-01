from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import create_app


def test_parse_document_from_data_dir(isolated_settings) -> None:
    settings = isolated_settings
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    sample_file = settings.data_dir / "sample.txt"
    sample_file.write_text("hello docling fallback", encoding="utf-8")

    with TestClient(create_app()) as client:
        response = client.post("/documents/parse", json={"source": "sample.txt"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "queued"

        job_response = client.get(f"/jobs/{payload['job_id']}")
        assert job_response.status_code == 200
        assert job_response.json()["status"] == "finished"

        doc_response = client.get(f"/documents/{payload['document_id']}")
        assert doc_response.status_code == 200
        assert doc_response.json()["chunk_count"] >= 1
