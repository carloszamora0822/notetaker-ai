# Sprint Tracker

**Current Sprint**: Sprint 0
**Sprint Goal**: Basic skeleton - all services can start without crashing

---

## Sprint 0 Status

### Backend (@dev-backend)
- [ ] `/health` endpoint returns `{"ok": true, "time": str}`
- [ ] `/ingest` saves files to inbox/ and returns JSON
- [ ] Reads `config/app.yaml` successfully
- [ ] Writes `logs/backend_status.json` every 30s
- [ ] Stub `/rag/query` returns placeholder response

**Branch**: `backend/initial`
**Status**: 🟡 In Progress
**Blockers**: None

---

### RAG (@dev-rag)
- [ ] Loads model from `config["embeddings"]["model_path"]`
- [ ] Prints `[OK] Model folder present` on startup
- [ ] Initializes Chroma DB in `rag/index/chroma/`
- [ ] Writes `logs/rag_status.json` every 30s
- [ ] `rag.get_status()` function exists and returns dict

**Branch**: `rag/initial`
**Status**: 🟡 In Progress
**Blockers**: Need embedding model downloaded

---

### LaTeX (@dev-latex)
- [ ] Watcher script compiles `latex/templates/default.tex`
- [ ] Produces PDF without errors
- [ ] Creates `latex/queue/` and `latex/output/` directories
- [ ] Writes `logs/latex_status.json` every 30s
- [ ] latexmk installed and working

**Branch**: `latex/initial`
**Status**: 🟡 In Progress
**Blockers**: None

---

### Frontend (@dev-frontend)
- [ ] `base.html` renders with navigation
- [ ] Upload form POSTs to `/ingest` endpoint
- [ ] Search form POSTs to `/rag/query` endpoint
- [ ] Basic CSS applied (no external CDN)
- [ ] Client-side validation on forms

**Branch**: `frontend/initial`
**Status**: 🟡 In Progress
**Blockers**: Waiting for backend endpoints

---

### Ops (@dev-ops)
- [ ] `make bootstrap` completes without errors
- [ ] `make dev` starts 5 tmux panes successfully
- [ ] Pre-commit hooks fire on commit
- [ ] `ops/scripts/check_health.sh` reports all services
- [ ] `docs/SETUP.md` created with instructions

**Branch**: `ops/initial`
**Status**: 🟡 In Progress
**Blockers**: None

---

## Sprint 0 Definition of Done

✅ **Integration Test**: `make dev` starts all 5 panes without crashes
✅ **Ingest Test**: `curl -F file=@sample.txt http://localhost:8000/ingest` succeeds
✅ **LaTeX Test**: Can manually produce PDF from `default.tex`
✅ **Status Files**: All 3 status JSON files (`backend`, `rag`, `latex`) exist and update
✅ **Health Check**: `make check-health` reports all services

---

## Sprint 1 Preview

### Backend
- Wire pipeline: ingest → RAG indexing → (optional) LaTeX generation
- Implement `/api/classes` endpoint
- Call `rag.search()` in `/rag/query`

### RAG
- Implement chunker (900/120 tokens)
- Implement `search()` function
- Implement `index_document()` function

### LaTeX
- Create `render.py` to convert JSON → .tex
- Process `latex/queue/` for input files
- Write result JSON after compilation

### Frontend
- Fetch API for forms (no page reload)
- Display RAG results with citations
- Class list view from `/api/classes`

### Ops
- Interface validation script
- Integration tests
- Logging setup

---

## Notes

- **Daily Standup**: Check this file and update your status
- **Blockers**: Add here immediately so Manager can resolve
- **Interface Issues**: Use `INTERFACE-REQUESTS.md`
