from __future__ import annotations

import json
import time
from urllib import error, request

API_BASE_URL = "http://127.0.0.1:8000"
SOURCE = "raw/\u5927\u81f4\u6846\u67b6.pdf"
TENANT_ID = "rag"
KNOWLEDGE_BASE_ID = "test"
METADATA: dict[str, object] = {}
POLL_INTERVAL_SECONDS = 2
MAX_POLLS = 60


def post_json(path: str, payload: dict[str, object]) -> dict[str, object]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{API_BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    return _read_json(req)


def get_json(path: str) -> dict[str, object]:
    req = request.Request(
        f"{API_BASE_URL}{path}",
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="GET",
    )
    return _read_json(req)


def _read_json(req: request.Request) -> dict[str, object]:
    try:
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> None:
    accepted = post_json(
        "/documents/index",
        {
            "source": SOURCE,
            "tenant_id": TENANT_ID,
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "metadata": METADATA,
        },
    )
    print("Accepted:")
    print(json.dumps(accepted, ensure_ascii=False, indent=2))

    job_id = str(accepted["job_id"])
    document_id = str(accepted["document_id"])

    for attempt in range(1, MAX_POLLS + 1):
        job = get_json(f"/jobs/{job_id}")
        status = str(job.get("status", "unknown"))
        print(f"[{attempt}/{MAX_POLLS}] job status = {status}")

        if status == "finished":
            document = get_json(f"/documents/{document_id}")
            print("Document:")
            print(json.dumps(document, ensure_ascii=False, indent=2))
            return

        if status == "failed":
            print("Job failed:")
            print(json.dumps(job, ensure_ascii=False, indent=2))
            return

        time.sleep(POLL_INTERVAL_SECONDS)

    print("Timed out while waiting for the indexing job to finish.")


if __name__ == "__main__":
    main()
