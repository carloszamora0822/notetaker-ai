# MANAGER GUIDE - Multi-IDE Coordination

**YOUR ROLE**: Enforce contracts, prevent hallucination, ensure harmony.

---

## Critical Rules to Enforce

### 1. **INTERFACE VIOLATIONS**
If ANY dev tries to:
- Import directly between areas (except documented contracts)
- Create new endpoints without updating `API-CONTRACTS.md`
- Hardcode paths instead of using `config/app.yaml`
- Skip writing status files

**ACTION**: REJECT and point them to `docs/API-CONTRACTS.md`

### 2. **HALLUCINATION DETECTION**
Watch for:
- "I'll call this function that should exist..."
- Making assumptions about other areas' implementation
- Creating phantom endpoints or methods

**ACTION**: Require them to check `docs/API-CONTRACTS.md` and return stubs with `# TODO` if not ready

### 3. **FILE OWNERSHIP**
```
backend/     → Backend dev ONLY
rag/         → RAG dev ONLY
latex/       → LaTeX dev ONLY
frontend/    → Frontend dev ONLY
ops/         → Ops dev ONLY
config/      → Ops dev ONLY (others READ-ONLY)
docs/        → Manager maintains
tests/       → Backend dev (initially)
```

**ACTION**: No dev touches another's folder without explicit coordination

---

## Daily Coordination Flow

### Morning (Sprint Start)
1. All devs read `docs/API-CONTRACTS.md`
2. Each dev creates branch: `git checkout -b <area>/<task>`
3. Each dev reads their `<area>/README-DEV.md`
4. Status check: `make check-interfaces`

### During Work
1. Monitor status files in `logs/`:
   - `rag_status.json`
   - `latex_status.json`
   - `backend_status.json`
2. Check for interface requests in `docs/INTERFACE-REQUESTS.md`
3. Review commits for cross-boundary violations

### Before Merge
1. Run `make check` (black, ruff, mypy)
2. Run `make test`
3. Verify status files update correctly
4. Check CODEOWNERS approval

---

## Communication Protocol

### New Interface Needed?
Dev writes to `docs/INTERFACE-REQUESTS.md`:
```markdown
## Request: [Area] needs [What]
**Requester**: Backend
**Provider**: RAG
**Need**: Get model info (name, size, version)
**Proposed**: Add `rag.get_model_info() -> Dict`
**Status**: PENDING APPROVAL
```

Manager reviews → approves → updates `API-CONTRACTS.md` → notifies both devs

### Integration Issue?
Dev writes to `logs/<area>_integration.log`:
```
[2025-09-30T23:00] Backend: Called rag.search(), got KeyError on 'chunk'
Expected: [{"chunk": str, "source": str}]
Got: [{"text": str, "file": str}]
```

Manager mediates → points to contract → dev fixes

---

## Sprint 0 Acceptance (Manager Validates)

### Backend
- [ ] `/health` returns `{"ok": true, "time": str}`
- [ ] `/ingest` writes to `inbox/` and returns JSON
- [ ] Reads `config/app.yaml` successfully
- [ ] Writes `logs/backend_status.json`

### RAG
- [ ] Loads model from `config["embeddings"]["model_path"]`
- [ ] `rag.get_status()` returns dict
- [ ] Writes `logs/rag_status.json` every 30s
- [ ] Prints `[OK] Model folder present` on startup

### LaTeX
- [ ] Watcher compiles `latex/templates/default.tex`
- [ ] Produces PDF without errors
- [ ] Writes `logs/latex_status.json`
- [ ] Monitors `latex/queue/` directory

### Frontend
- [ ] `base.html` renders with `{% block content %}`
- [ ] Upload form POSTs to `/ingest`
- [ ] Chat box POSTs to `/rag/query`
- [ ] No hardcoded URLs (uses form action)

### Ops
- [ ] `make bootstrap` completes without errors
- [ ] `make dev` starts 5 tmux panes
- [ ] Pre-commit hooks fire on commit
- [ ] All devs can read `config/app.yaml`

---

## Sprint 1 Integration Points (Manager Validates)

### Backend → RAG Integration
```python
# Backend code
from rag.search import search
results = search("test query", top_k=8)
assert isinstance(results, list)
assert "chunk" in results[0]
```

### Backend → LaTeX Integration
```python
# Backend writes
input_file = Path("latex/queue/2025-09-30_CS101_input.json")
input_file.write_text(json.dumps({"summary": "test", ...}))

# LaTeX produces
output_file = Path("latex/output/CS101.pdf")
result_file = Path("latex/queue/2025-09-30_CS101_result.json")
```

### Frontend → Backend Integration
```bash
# Test upload
curl -F file=@sample.txt -F class_code=TEST http://localhost:8000/ingest
# Expected: {"stored": "...", "receipt_id": "..."}

# Test query
curl -X POST http://localhost:8000/rag/query -H "Content-Type: application/json" -d '{"q":"test"}'
# Expected: {"answer": "...", "citations": [...]}
```

---

## Red Flags 🚨

1. **"I think it should work..."** → NO. Test it.
2. **"The other service will handle..."** → Verify interface exists.
3. **"Let me just quickly import..."** → Check API-CONTRACTS first.
4. **Silent failures** → Require status file updates.
5. **"Works on my machine"** → Verify via shared status files.

---

## Conflict Resolution

### Merge Conflict
1. Check CODEOWNERS - did someone cross boundaries?
2. If same file: `git rerere` should auto-resolve repeats
3. If interface dispute: Enforce contract, reject both PRs until aligned

### Interface Disagreement
1. Call "interface meeting" (all affected devs)
2. Reference `API-CONTRACTS.md`
3. Manager makes final decision
4. Update contracts BEFORE any dev proceeds

### Performance Issue
1. Check `config/app.yaml` → is RAM budget exceeded?
2. Review logs for bottlenecks
3. Ops dev investigates with `ops/scripts/check_health.sh`

---

## Daily Manager Commands

```bash
# Morning: Check all status files
cat logs/*_status.json | jq '.'

# Monitor integration
tail -f logs/*.log

# Verify interfaces
python ops/scripts/check_interfaces.py

# Before sprint demo
make check && make test
```

---

## Success Criteria

✅ All 5 areas can work in parallel without blocking
✅ No direct imports outside contracts
✅ Status files update reliably
✅ Merge conflicts rare (<1 per day)
✅ Integration tests pass
✅ `make dev` starts all services successfully
