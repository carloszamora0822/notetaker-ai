# API CONTRACTS & INTERFACE SPECIFICATIONS

**CRITICAL**: These are the ONLY ways components communicate. DO NOT deviate.

## 1. Backend ↔ Frontend

### HTTP Endpoints (Backend MUST implement, Frontend MUST use)

```python
# Health Check
GET /health
Response: {"ok": bool, "time": str}

# Ingest Document
POST /ingest
Form Data:
  - file: UploadFile (required)
  - class_code: str (optional, default="unknown")
Response: {"stored": str, "receipt_id": str}

# RAG Query
POST /rag/query
JSON Body: {"q": str, "scope": str}
Response: {
  "answer": str,
  "citations": [{"chunk": str, "source": str, "score": float}]
}

# List Classes
GET /api/classes
Response: {"classes": [{"code": str, "name": str, "count": int}]}
```

---

## 2. Backend ↔ RAG

### Python Function Interface (NO HTTP)

```python
# Module: rag.search
from typing import List, Dict

def search(query: str, top_k: int = 8, scope: str = "all") -> List[Dict]:
    """
    Args:
        query: search text
        top_k: number of results
        scope: "all" | class_code
    Returns:
        [{"chunk": str, "source": str, "score": float, "citation": str}, ...]
    """
    pass

def index_document(text: str, metadata: Dict) -> bool:
    """
    Args:
        text: document content
        metadata: {"class_code": str, "date": str, "filename": str}
    Returns:
        True on success
    """
    pass

def get_status() -> Dict:
    """
    Returns: {"model_loaded": bool, "index_size": int, "ready": bool}
    """
    pass
```

**File Contract**: RAG writes status to `logs/rag_status.json` every 30 seconds.

---

## 3. Backend ↔ LaTeX

### File-Based Interface (NO Python imports)

```python
# Backend writes:
# File: latex/queue/{timestamp}_{class_code}_input.json
{
  "summary": str,           # main content
  "metadata": {
    "class_code": str,
    "date": str,
    "title": str,
    "sections": [{"heading": str, "content": str}]
  },
  "output_name": str        # desired PDF name
}

# LaTeX renderer reads queue/, produces:
# File: latex/output/{output_name}.pdf
# File: latex/queue/{timestamp}_{class_code}_result.json
{
  "success": bool,
  "pdf_path": str | null,
  "error": str | null,
  "compile_time_sec": float
}
```

**Watcher**: LaTeX watcher monitors `latex/queue/` for `*_input.json` files.

---

## 4. Shared State Files (ALL components read, ONLY owner writes)

### `logs/rag_status.json` (RAG writes, Backend reads)
```json
{
  "timestamp": "2025-09-30T23:00:00",
  "model_loaded": true,
  "index_size": 1234,
  "ready": true,
  "last_error": null
}
```

### `logs/latex_status.json` (LaTeX writes, Backend reads)
```json
{
  "timestamp": "2025-09-30T23:00:00",
  "watcher_running": true,
  "queue_size": 2,
  "last_compile": {"file": "CS101.pdf", "success": true}
}
```

### `logs/backend_status.json` (Backend writes, Ops reads)
```json
{
  "timestamp": "2025-09-30T23:00:00",
  "server_running": true,
  "port": 8000,
  "requests_handled": 42
}
```

---

## 5. Configuration (ALL read, ONLY Ops writes)

### `config/app.yaml` - Single Source of Truth

```yaml
timezone: "America/Chicago"
offline_mode: true
ram_budget_gb: 10

paths:
  inbox_global: "./inbox"
  semesters_root: "./semesters"
  models_root: "./rag/models"
  latex_queue: "./latex/queue"
  latex_output: "./latex/output"

embeddings:
  model_path: "./rag/models/bge-small-en-v1.5"
  chunk_tokens: 900
  overlap_tokens: 120

rag:
  top_k: 8
  with_reranker: false

latex:
  engine: "xelatex"
  compile_cmd: "latexmk -xelatex -halt-on-error -interaction=nonstopmode"
  template: "default"
```

---

## RULES FOR ALL DEVS

1. **NO DIRECT IMPORTS** between Backend/RAG/LaTeX except as specified above
2. **USE ONLY** these interfaces - if you need more, request via `docs/INTERFACE-REQUESTS.md`
3. **VALIDATE** all inputs at boundaries
4. **WRITE STATUS** files on schedule
5. **READ CONFIG** from `config/app.yaml` - never hardcode paths
6. **LOG ERRORS** to `logs/{area}.log` with timestamps
7. **NO HALLUCINATION** - if interface doesn't exist yet, return stub with TODO comment

---

## Verification Checklist

- [ ] Backend can call `rag.search()` and get list of dicts
- [ ] Backend writes JSON to `latex/queue/`, LaTeX processes it
- [ ] Frontend POSTs to `/ingest` and gets JSON response
- [ ] Status files update every 30 seconds
- [ ] All paths come from `config/app.yaml`
