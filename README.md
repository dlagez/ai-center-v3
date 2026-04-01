# AI Center V3

当前仓库内的文档处理子系统代码位于 `src/`。

## 启动

```bash
uvicorn src.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 当前实现

- 输入源来自 `data/` 目录或 URL
- 解析链路当前固定为 Docling
- 当本地未安装 `langchain-docling` 时，对文本类文件启用轻量 fallback
- 元数据落 SQLite
- 向量落本地 Qdrant
- `processing`、`retrieval`、`rag` 已分离

## RAG 使用

### 1. 先写入索引

把待处理文件放到 `data/` 目录后，调用：

```bash
curl -X POST "http://127.0.0.1:8000/documents/index" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"sample.txt\",\"tenant_id\":\"t1\",\"knowledge_base_id\":\"kb_finance\"}"
```

返回里会包含：

- `job_id`
- `document_id`
- `status`

查看任务状态：

```bash
curl "http://127.0.0.1:8000/jobs/<job_id>"
```

查看文档状态：

```bash
curl "http://127.0.0.1:8000/documents/<document_id>"
```

### 2. 执行 RAG 查询

```bash
curl -X POST "http://127.0.0.1:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"报销制度里差旅补贴标准是什么？\",\"top_k\":5,\"metadata_filter\":{\"tenant_id\":\"t1\",\"knowledge_base_id\":\"kb_finance\"}}"
```

返回内容包括：

- `answer`
- `citations`

### 3. 直接检索

如果只想看召回结果，不生成答案：

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"差旅补贴标准\",\"top_k\":5,\"metadata_filter\":{\"tenant_id\":\"t1\"}}"
```

## 当前限制

- `rag/answer_chain.py` 目前是可运行占位实现，还没有接真实大模型
- `processing/chunking` 仍是预留目录，当前主链路直接使用 Docling 输出的 `DOC_CHUNKS`
- `processing/normalize` 目前只做轻量校验和 metadata 补全
- 当前 `processing/loaders/` 只实现了 `docling_loader.py`

## 测试

```bash
python -m pytest -q
```
