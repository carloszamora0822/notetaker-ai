# Individual Developer Prompts - Next Actions

**Manager**: Copy the relevant prompt and paste it into each developer's window.

---

## 🔧 BACKEND DEVELOPER - Critical Fixes Required

### What You've Done Well ✅
- Implemented `/health` endpoint correctly
- Implemented `/ingest` endpoint - working perfectly (2 uploads tested)
- Added status file writer with background tasks
- Server is running successfully on port 8000

### Critical Issues Found 🚨

**ISSUE 1: Contract Violation - `/rag/query` endpoint**

Your current code (line 79-91) uses `Form` but Frontend sends JSON:

```python
# WRONG - Current code
@app.post("/rag/query")
async def rag_query(q: str = Form(...), scope: str = Form("all")):
```

**FIX THIS NOW** - Replace lines 79-91 with:

```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    q: str
    scope: str = "all"

@app.post("/rag/query")
async def rag_query(request: QueryRequest):
    """RAG query endpoint - Sprint 0 stub
    
    TODO: Call rag.search() in Sprint 1
    """
    global request_counter
    request_counter += 1
    
    return {
        "answer": "Not implemented yet",
        "citations": []
    }
```

**ISSUE 2: Static files not served**

Add this after line 18 in `backend/main.py`:

```python
from fastapi.staticfiles import StaticFiles

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
```

**ISSUE 3: Missing template routes**

Add these routes after the `/health` endpoint:

```python
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Serve upload page"""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Serve search page"""
    return templates.TemplateResponse("search.html", {"request": request})
```

**ISSUE 4: Not reading config**

Replace line 65-66 (hardcoded inbox path) with:

```python
import yaml

# At top of file, load config
CONFIG_PATH = BASE_DIR / "config" / "app.yaml"
if CONFIG_PATH.exists():
    CFG = yaml.safe_load(CONFIG_PATH.read_text())
else:
    CFG = {"paths": {"inbox_global": "./inbox"}}  # Fallback

# In ingest function, use config:
inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
```

### Your Tasks (30 minutes)

1. **Apply all 4 fixes above** to `backend/main.py`
2. **Restart your server**: Stop current backend, run `make backend` again
3. **Test these URLs** in browser:
   - http://localhost:8000/upload (should show upload form)
   - http://localhost:8000/search (should show search form)
4. **Test upload** with curl: `curl -F file=@test.txt http://localhost:8000/ingest`
5. **Commit your changes**: `git add backend/main.py && git commit -m "fix(backend): contract compliance and static files"`

### Verification

After fixes, run this:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/upload  # Should return HTML
curl -X POST http://localhost:8000/rag/query -H "Content-Type: application/json" -d '{"q":"test"}'
```

All should work without errors.

---

## 🧠 RAG DEVELOPER - Excellent Work, One Task Remains

### What You've Done ✅
- **PERFECT** implementation of `search.py` - 100% contract compliant
- **PERFECT** implementation of `indexer.py` - robust error handling
- Implemented `chunker.py` correctly
- Created test file
- Excellent logging throughout
- Status file writer working

### Current Status
Your code is **complete and correct**. The only issue is the embedding model is missing.

**Current error** (from `logs/rag_status.json`):
```json
{
  "model_loaded": false,
  "index_size": 0,
  "ready": false,
  "last_error": "Model failed to load"
}
```

### Your Task (5 minutes download + 2 minutes test)

**1. Download the embedding model** (one-time, ~500MB):

```bash
cd /path/to/notetaker-ai
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
print("Downloading bge-small-en-v1.5 model...")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
model.save('rag/models/bge-small-en-v1.5')
print("✓ Model saved to rag/models/bge-small-en-v1.5/")
EOF
```

**2. Verify model exists**:

```bash
ls -la rag/models/bge-small-en-v1.5/
# Should see: config.json, model.safetensors, tokenizer files
```

**3. Test your code**:

```bash
python3 rag/indexer.py
```

**Expected output**:
```
[OK] Model folder present: /path/to/rag/models/bge-small-en-v1.5
Loading embedding model...
[OK] Model loaded: 384 dims
[OK] Vector store ready: 0 documents
✅ RAG System Initialization Complete!
```

**4. Test indexing** (in Python):

```python
from rag.search import index_document, search

# Test indexing
metadata = {"class_code": "TEST", "date": "2025-09-30", "filename": "test.txt"}
success = index_document("This is a test document about AI.", metadata)
print(f"Index success: {success}")

# Test search
results = search("AI", top_k=3)
print(f"Search results: {results}")
```

**5. Commit**:

```bash
# Don't commit the model (too big, in .gitignore)
git add rag/
git commit -m "feat(rag): complete RAG implementation with search and indexing"
```

### Verification

Check `logs/rag_status.json` should show:
```json
{
  "model_loaded": true,
  "index_size": <number>,
  "ready": true,
  "last_error": null
}
```

**You're done!** Your code is excellent. Just needed the model file.

---

## 📝 LATEX DEVELOPER - Complete, Ready to Test

### What You've Done ✅
- Created professional `default.tex` template
- Created `compile_watch.sh` watcher script
- Created `render.py` for JSON → .tex conversion
- All files are well-structured

### Current Status
Your code is **complete**. Not running yet, but ready to test.

### Your Tasks (15 minutes)

**1. Verify LaTeX is installed**:

```bash
which latexmk
# If not found: brew install --cask basictex
# Then restart terminal
```

**2. Test manual compilation**:

```bash
cd latex/templates
latexmk -xelatex -halt-on-error -interaction=nonstopmode default.tex
```

**Expected**: Should create `default.pdf` without errors

**3. Create a test LaTeX template**:

```bash
cat > latex/templates/test_lecture.tex << 'EOF'
\documentclass[11pt]{article}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{xcolor}

\definecolor{ClassColor}{HTML}{0B72B9}

\begin{document}

\title{Test Lecture - CS101}
\date{2025-09-30}
\maketitle

\section{Introduction}

This is a test lecture generated by the LaTeX system.

\subsection{Key Points}
\begin{itemize}
  \item Point one about algorithms
  \item Point two about data structures
  \item Point three about complexity
\end{itemize}

\end{document}
EOF
```

**4. Compile test template**:

```bash
cd latex/templates
latexmk -xelatex test_lecture.tex
ls -la *.pdf
```

**5. Test the watcher** (run in background):

```bash
cd /path/to/notetaker-ai
bash latex/scripts/compile_watch.sh &
```

**6. Create status file writer**:

Add to `latex/scripts/compile_watch.sh` (inside the while loop):

```bash
# Update status file
cat > logs/latex_status.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "watcher_running": true,
  "queue_size": $(ls latex/queue/*_input.json 2>/dev/null | wc -l | xargs),
  "last_compile": {"file": "$(ls -t latex/output/*.pdf 2>/dev/null | head -1 | xargs basename)", "success": true}
}
EOF
```

**7. Test queue processing**:

Create a test job:
```bash
cat > latex/queue/test_input.json << 'EOF'
{
  "summary": "This is a test summary about algorithms and data structures.",
  "metadata": {
    "class_code": "CS101",
    "date": "2025-09-30",
    "title": "Test Lecture"
  },
  "output_name": "test_cs101"
}
EOF
```

Wait a few seconds, then check:
```bash
ls latex/output/test_cs101.pdf
ls latex/queue/test_result.json
```

**8. Commit**:

```bash
git add latex/
git commit -m "feat(latex): complete LaTeX rendering system with watcher"
```

### Verification

- [ ] `default.pdf` generated successfully
- [ ] Watcher runs without errors
- [ ] `logs/latex_status.json` exists and updates
- [ ] Queue processing works (test PDF generated)

**You're done!** Ready for integration.

---

## 🎨 FRONTEND DEVELOPER - Perfect! No Changes Needed

### What You've Done ✅
- Created beautiful `base.html` with navigation
- Created `upload.html` with file upload form
- Created `search.html` with search interface
- Created `main.css` with professional styling (132 lines)
- Created `main.js` with async fetch handlers (79 lines)
- **PERFECT** contract compliance - uses exact endpoints from API-CONTRACTS.md
- Responsive design implemented
- Error handling implemented
- No external CDNs (fully offline)

### Current Status
**100% COMPLETE** - Sprint 0 & Sprint 1 done!

### Your Task (5 minutes - verification only)

**Just verify your work is ready**:

1. Check all files exist:
```bash
ls frontend/templates/base.html
ls frontend/templates/upload.html
ls frontend/templates/search.html
ls frontend/static/css/main.css
ls frontend/static/js/main.js
```

2. Verify contract compliance:
```bash
# Your code uses:
# - POST /ingest with FormData ✓
# - POST /rag/query with JSON {"q", "scope"} ✓
# Both match docs/API-CONTRACTS.md perfectly!
```

3. Commit your work:
```bash
git add frontend/
git commit -m "feat(frontend): complete UI with upload, search, and responsive design"
```

### Integration Test (when backend is fixed)

Once backend applies their fixes, test in browser:

1. Visit: http://localhost:8000/upload
2. Upload a text file
3. Visit: http://localhost:8000/search
4. Search for something

**You're done!** Excellent work. No changes needed.

---

## ⚙️ OPS DEVELOPER - Infrastructure Ready, Runtime Tasks Needed

### What You've Done ✅
- Created all operational scripts (`check_health.sh`, `bootstrap_mac.sh`, `check_interfaces.py`)
- Created `.gitignore` (comprehensive)
- Created directory structure
- Documentation complete

### Current Status
Infrastructure is **complete**. Need to execute runtime tasks.

### Your Tasks (20 minutes)

**1. Create `config/app.yaml`**:

```bash
cat > config/app.yaml << 'EOF'
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
  model_path: "./rag/models/bge-small-en-v1.5"
  chunk_size: 500
  chunk_overlap: 50
  index_path: "./rag/index/chroma"
  collection_name: "notes"
  max_results: 8

latex:
  engine: "xelatex"
  compile_cmd: "latexmk -xelatex -halt-on-error -interaction=nonstopmode"
  template: "default"
EOF
```

**2. Run bootstrap** (if not done yet):

```bash
source .venv/bin/activate
make bootstrap
```

**3. Download embedding model** (if RAG dev hasn't):

```bash
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
model.save('rag/models/bge-small-en-v1.5')
print("✓ Model downloaded")
EOF
```

**4. Run health check**:

```bash
bash ops/scripts/check_health.sh
```

**5. Run interface validation**:

```bash
python3 ops/scripts/check_interfaces.py
```

**6. Create `docs/SETUP.md`**:

```bash
cat > docs/SETUP.md << 'EOF'
# Setup Guide

## Prerequisites (macOS)

Run automated setup:
```bash
bash ops/scripts/bootstrap_mac.sh
```

Or manually install:
- Python 3.11+
- BasicTeX: `brew install --cask basictex`
- tmux: `brew install tmux`
- jq: `brew install jq`

## First Time Setup

1. Clone repository
2. Create virtual environment: `python3 -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `make bootstrap`
5. Download model: See README.md

## Running

```bash
# All services
make dev

# Individual services
make backend  # Port 8000
make rag      # Background
make latex    # Watcher
```

## Health Check

```bash
make check-health
make check-status
```

## Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### LaTeX not compiling
```bash
which latexmk
brew install --cask basictex
```

### RAG model missing
Download: https://huggingface.co/BAAI/bge-small-en-v1.5
Place in: `rag/models/bge-small-en-v1.5/`
EOF
```

**7. Test tmux workspace**:

```bash
# This should start all services
bash ops/scripts/devmux.sh
```

**8. Monitor everything**:

```bash
# In one terminal
watch -n 5 'cat logs/*_status.json | jq .'

# In another
tail -f logs/*.log
```

**9. Commit**:

```bash
git add config/ ops/ docs/SETUP.md
git commit -m "feat(ops): complete operational infrastructure with config and scripts"
```

### Verification Checklist

- [ ] `config/app.yaml` exists and valid
- [ ] `make bootstrap` completes successfully
- [ ] `make check-health` reports all services
- [ ] `make check-interfaces` passes
- [ ] Embedding model downloaded
- [ ] `docs/SETUP.md` created

**You're done!** System is fully operational.

---

## 📋 MANAGER (You) - Coordination Tasks

### Monitor Progress

Check each developer's status:

```bash
# Backend
curl http://localhost:8000/health

# RAG
cat logs/rag_status.json | jq '.ready'

# LaTeX
cat logs/latex_status.json | jq '.watcher_running'

# Frontend
curl http://localhost:8000/upload  # Should return HTML
```

### Integration Test (when all devs done)

```bash
# 1. Upload a document
echo "Test content about algorithms" > test.txt
curl -F file=@test.txt -F class_code=CS101 http://localhost:8000/ingest

# 2. Search for it
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"q":"algorithms","scope":"all"}'

# 3. Check LaTeX queue (future)
```

### When to Merge

Merge each developer's branch when:
- [ ] Their tasks above are complete
- [ ] `make check-interfaces` passes
- [ ] Their status file updates correctly
- [ ] Integration tests pass

---

## 🎯 Timeline Estimate

| Developer | Time Needed | Complexity |
|-----------|-------------|------------|
| Backend | 30 min | Medium - 4 fixes |
| RAG | 7 min | Easy - just download |
| LaTeX | 15 min | Easy - just testing |
| Frontend | 5 min | Trivial - verification |
| Ops | 20 min | Medium - config + setup |

**Total**: ~75 minutes to full Sprint 0 completion!
