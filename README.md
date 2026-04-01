# AI Center V3

Document parsing, indexing, retrieval, and RAG service built with FastAPI, SQLite, Qdrant, Docling, and LiteLLM.

## Start

```bash
uvicorn --env-file .env src.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Model Configuration

The project now uses LiteLLM for both embeddings and RAG answer generation.

Copy `.env.example` to `.env`, then set the model-related variables:

```env
LITELLM_API_KEY=your_api_key
LITELLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LITELLM_CHAT_MODEL=openai/qwen-plus
LITELLM_EMBEDDING_MODEL=openai/text-embedding-v4
EMBEDDING_DIMENSIONS=1024
LITELLM_EMBEDDING_BATCH_SIZE=10
```

Notes:

- The example above targets DashScope through its OpenAI-compatible endpoint.
- `EMBEDDING_DIMENSIONS` must match the actual embedding output dimension written into Qdrant.
- If you change the embedding model or dimension, clear the existing local Qdrant collection data before re-indexing.
- `LITELLM_EMBEDDING_BATCH_SIZE` should stay within the provider's batch limit.

## Index a Document

Place the source file under `data/`, then call:

```bash
curl -X POST "http://127.0.0.1:8000/documents/index" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"sample.txt\",\"tenant_id\":\"t1\",\"knowledge_base_id\":\"kb_finance\"}"
```

The response includes:

- `job_id`
- `document_id`
- `status`

Check job status:

```bash
curl "http://127.0.0.1:8000/jobs/<job_id>"
```

Check document status:

```bash
curl "http://127.0.0.1:8000/documents/<document_id>"
```

## Search

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"travel reimbursement standard\",\"top_k\":5,\"metadata_filter\":{\"tenant_id\":\"t1\"}}"
```

## RAG Query

```bash
curl -X POST "http://127.0.0.1:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What is the travel reimbursement standard?\",\"top_k\":5,\"metadata_filter\":{\"tenant_id\":\"t1\",\"knowledge_base_id\":\"kb_finance\"}}"
```

The response includes:

- `answer`
- `citations`

## Current Scope

- Input source can be a file under `data/` or a URL.
- Docling is the only parsing path in the current implementation.
- `processing/chunking` is still reserved; the main path indexes Docling `DOC_CHUNKS` directly.
- `processing/normalize` only handles light validation and metadata completion.
- Metadata is stored in SQLite and vectors are stored in local Qdrant.

## Test

```bash
python -m pytest -q
```
