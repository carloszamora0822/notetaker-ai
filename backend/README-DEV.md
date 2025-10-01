# Backend Developer Guide

**Your Role**: FastAPI app orchestrating ingest, RAG proxy, and LaTeX pipeline.

---

## Your Workspace

```bash
cd /path/to/notetaker-ai/backend
source ../.venv/bin/activate
```

**Files you OWN**:
- `backend/app/main.py` - FastAPI application
- `backend/cli/` - CLI tools (future)
- `tests/` - Pytest tests

**Files you READ** (do NOT edit):
- `config/app.yaml` - Configuration
- `logs/rag_status.json` - RAG health
- `logs/latex_status.json` - LaTeX health

---

## Sprint 0 Tasks (2-4 hours)

### Task 1: Implement `/health` endpoint
```python
@app.get("/health")
def health():
    return {"ok": True, "time": datetime.now().isoformat()}
```
**Test**: `curl http://localhost:8000/health`

### Task 2: Implement `/ingest` endpoint
- Accept file upload + optional `class_code`
- Read `config/app.yaml` for inbox path
- Write file to `inbox/{date}_{class_code}.txt`
- Return `{"stored": str, "receipt_id": str}`

**Test**: `curl -F file=@test.txt http://localhost:8000/ingest`

### Task 3: Write status file
- Create `logs/backend_status.json` on startup
- Update every 30 seconds with: `{"server_running": true, "port": 8000, "requests_handled": N}`

### Task 4: Stub `/rag/query`
```python
@app.post("/rag/query")
async def rag_query(q: str, scope: str = "all"):
    # TODO: Call rag.search() in Sprint 1
    return {"answer": "Not implemented yet", "citations": []}
```

**Acceptance**:
- [ ] `make backend` starts server on port 8000
- [ ] `/health` returns 200
- [ ] `/ingest` saves files to inbox/
- [ ] `logs/backend_status.json` exists and updates

---

## Sprint 1 Tasks (4-8 hours)

### Task 1: Integrate RAG
```python
from rag.search import search, get_status

@app.post("/rag/query")
async def rag_query(q: str, scope: str = "all"):
    # Check RAG is ready
    status = get_status()
    if not status["ready"]:
        raise HTTPException(503, "RAG not ready")

    results = search(q, top_k=8, scope=scope)
    return {"answer": results[0]["chunk"] if results else "", "citations": results}
```

### Task 2: Build ingest pipeline
```python
@app.post("/ingest")
async def ingest_txt(file: UploadFile, class_code: str = Form("")):
    # 1. Save to inbox
    text = (await file.read()).decode()
    inbox_path = save_to_inbox(text, class_code)

    # 2. Index with RAG
    from rag.search import index_document
    success = index_document(text, {
        "class_code": class_code,
        "date": str(date.today()),
        "filename": file.filename
    })

    # 3. Trigger LaTeX (optional for Sprint 1)
    # Write to latex/queue/ if summary available

    return {"stored": str(inbox_path), "receipt_id": f"{date.today()}_{class_code}"}
```

### Task 3: LaTeX pipeline (file-based)
```python
def trigger_latex_render(summary: str, class_code: str):
    """Write input JSON for LaTeX to process"""
    queue_path = Path(CFG["paths"]["latex_queue"])
    input_file = queue_path / f"{datetime.now().timestamp()}_{class_code}_input.json"

    input_file.write_text(json.dumps({
        "summary": summary,
        "metadata": {"class_code": class_code, "date": str(date.today())},
        "output_name": f"{class_code}_{date.today()}"
    }))
```

### Task 4: Implement `/api/classes`
```python
@app.get("/api/classes")
def list_classes():
    # Scan inbox/ or semesters/ for class codes
    classes = scan_classes()
    return {"classes": classes}
```

**Acceptance**:
- [ ] `/rag/query` returns real results from RAG
- [ ] `/ingest` triggers indexing
- [ ] Writing to `latex/queue/` produces PDF (LaTeX must be running)
- [ ] Tests pass: `pytest tests/`

---

## Interface Contract (READ-ONLY)

See `docs/API-CONTRACTS.md` for full spec. You MUST follow:

### You PROVIDE (HTTP):
- `GET /health`
- `POST /ingest`
- `POST /rag/query`
- `GET /api/classes`

### You CONSUME:
- `rag.search(query, top_k, scope) -> List[Dict]`
- `rag.index_document(text, metadata) -> bool`
- `rag.get_status() -> Dict`

### You WRITE:
- `logs/backend_status.json` (every 30s)
- `latex/queue/*_input.json` (per render)

---

## Development Loop

```bash
# Start backend
make backend

# In another terminal: test
curl http://localhost:8000/health
curl -F file=@sample.txt http://localhost:8000/ingest

# Run tests
pytest tests/ -v

# Format and lint
black . && ruff . --fix

# Before commit
pre-commit run --all-files
git add -A && git commit -m "feat(backend): <what you did>"
```

---

## Debugging

### RAG not responding?
Check `logs/rag_status.json`:
```bash
cat logs/rag_status.json | jq '.ready'
```
If `false`, coordinate with RAG dev.

### LaTeX not compiling?
Check `logs/latex_status.json`:
```bash
cat logs/latex_status.json | jq '.watcher_running'
```
Verify `latex/queue/` directory exists.

### Frontend can't reach you?
Check CORS (if needed) and verify port 8000 is accessible.

---

## Rules (DO NOT VIOLATE)

1. ✅ Read config from `config/app.yaml` - never hardcode paths
2. ✅ Import RAG as `from rag.search import ...` - do NOT modify RAG code
3. ✅ Write LaTeX jobs to `latex/queue/` - do NOT call LaTeX directly
4. ✅ Update `logs/backend_status.json` every 30s
5. ❌ Do NOT import Frontend, LaTeX, or Ops modules
6. ❌ Do NOT create new endpoints without updating `docs/API-CONTRACTS.md`

---

## Need Help?

1. Check `docs/API-CONTRACTS.md` for interfaces
2. Write issue to `docs/INTERFACE-REQUESTS.md`
3. Check status files in `logs/`
4. Ask Manager (main IDE instance)
