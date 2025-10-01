# Multi-Window IDE Setup Guide

**Purpose**: How to open separate IDE windows for each developer role.

---

## Setup Instructions

### Window 1: MANAGER (YOU - Main Window)
**Location**: `/Users/carloszamora/Desktop/notetaker-ai`
**Role**: Oversee all, enforce contracts, coordinate
**Files to Monitor**:
- `docs/MANAGER-GUIDE.md` - Your rulebook
- `docs/API-CONTRACTS.md` - The law
- `docs/SPRINT-TRACKER.md` - Status updates
- `docs/INTERFACE-REQUESTS.md` - Dev requests
- `logs/*_status.json` - Service health

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Monitor status
watch -n 5 'cat logs/*_status.json | jq .'

# Monitor logs
tail -f logs/*.log

# Check interfaces
python ops/scripts/check_interfaces.py
```

---

### Window 2: BACKEND Developer
**Location**: `/Users/carloszamora/Desktop/notetaker-ai/backend`
**Role**: FastAPI app, orchestration
**Primary Files**:
- `backend/README-DEV.md` - Your guide
- `backend/app/main.py` - Main application

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Read your guide first
cat backend/README-DEV.md

# Work on your branch
git checkout -b backend/initial

# Run service
make backend

# Test
curl http://localhost:8000/health
```

---

### Window 3: RAG Developer
**Location**: `/Users/carloszamora/Desktop/notetaker-ai/rag`
**Role**: Embeddings, vector store, search
**Primary Files**:
- `rag/README-DEV.md` - Your guide
- `rag/indexer.py` - Indexing logic
- `rag/search.py` - Search API (Sprint 1)

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Read your guide first
cat rag/README-DEV.md

# Work on your branch
git checkout -b rag/initial

# Run service
make rag

# Test
python -c "from rag.indexer import *"
```

**CRITICAL**: Place embedding model in `rag/models/bge-small-en-v1.5/` first!

---

### Window 4: LATEX Developer
**Location**: `/Users/carloszamora/Desktop/notetaker-ai/latex`
**Role**: Template rendering, PDF compilation
**Primary Files**:
- `latex/README-DEV.md` - Your guide
- `latex/scripts/compile_watch.sh` - Watcher
- `latex/templates/default.tex` - Default template

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Read your guide first
cat latex/README-DEV.md

# Work on your branch
git checkout -b latex/initial

# Run watcher
make latex

# Test manually
cd latex/templates && latexmk -xelatex default.tex
```

---

### Window 5: FRONTEND Developer
**Location**: `/Users/carloszamora/Desktop/notetaker-ai/frontend`
**Role**: UI templates, forms, CSS/JS
**Primary Files**:
- `frontend/README-DEV.md` - Your guide
- `frontend/templates/*.html` - Jinja templates
- `frontend/static/css/main.css` - Styles

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Read your guide first
cat frontend/README-DEV.md

# Work on your branch
git checkout -b frontend/initial

# Backend must be running to view
# In browser: http://localhost:8000
```

**NOTE**: Frontend needs Backend running to see changes!

---

### Window 6: OPS Developer
**Location**: `/Users/carloszamora/Desktop/notetaker-ai/ops`
**Role**: Tooling, health checks, coordination
**Primary Files**:
- `ops/README-DEV.md` - Your guide
- `ops/scripts/*.sh` - Operational scripts
- `config/app.yaml` - Configuration (you own this)

**Commands**:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
source .venv/bin/activate

# Read your guide first
cat ops/README-DEV.md

# Work on your branch
git checkout -b ops/initial

# Run checks
make check-health
make check-status

# Watch services
tmux attach -t notetaker
```

---

## Opening Windows (macOS)

### Option 1: Manual
1. Open 6 terminal windows
2. In each, `cd` to appropriate directory
3. Follow commands above for that role

### Option 2: Automated (Recommended)
```bash
# From main window
osascript << 'EOF'
tell application "Terminal"
  # Manager window (already open)

  # Backend
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat backend/README-DEV.md"

  # RAG
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat rag/README-DEV.md"

  # LaTeX
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat latex/README-DEV.md"

  # Frontend
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat frontend/README-DEV.md"

  # Ops
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat ops/README-DEV.md"
end tell
EOF
```

---

## Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      MANAGER (Window 1)                      │
│  - Monitors all status files                                 │
│  - Enforces API-CONTRACTS.md                                 │
│  - Reviews INTERFACE-REQUESTS.md                             │
│  - Updates SPRINT-TRACKER.md                                 │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   BACKEND     │   │      RAG      │   │     LATEX     │
│  (Window 2)   │◄─►│  (Window 3)   │   │  (Window 4)   │
│               │   │               │   │               │
│  HTTP Server  │   │  Python API   │   │  File Queue   │
└───────────────┘   └───────────────┘   └───────────────┘
        ▲                                       ▲
        │                                       │
        │           ┌───────────────┐          │
        └──────────►│   FRONTEND    │          │
                    │  (Window 5)   │          │
                    │               │          │
                    │  HTTP Client  │          │
                    └───────────────┘          │
                                              │
                    ┌───────────────┐         │
                    │      OPS      │─────────┘
                    │  (Window 6)   │
                    │               │
                    │  Monitoring   │
                    └───────────────┘
```

---

## Rules for All Windows

1. **READ your `README-DEV.md` FIRST** - Don't skip this!
2. **Stay in your folder** - Don't edit other areas
3. **Follow API-CONTRACTS.md** - No exceptions
4. **Update status files** - Every 30 seconds
5. **Request interface changes** - Use `INTERFACE-REQUESTS.md`
6. **Commit often** - Small, focused commits
7. **Test locally** - Before committing

---

## Daily Workflow

### Morning (All Windows)
1. `git pull --rebase`
2. `source .venv/bin/activate`
3. Read your `README-DEV.md`
4. Check `docs/SPRINT-TRACKER.md`
5. Create/checkout your branch

### During Work
1. Write code in your area ONLY
2. Update your status file
3. Test your endpoints/interfaces
4. Check `docs/INTERFACE-REQUESTS.md` for changes

### Before Commit
1. `pre-commit run --all-files`
2. Test your changes
3. Update `docs/SPRINT-TRACKER.md` (Manager does this)
4. `git commit -m "feat(<area>): <what>"`

---

## Troubleshooting

### "I can't see other devs' changes"
- Check status files: `cat logs/*_status.json`
- Verify service is running: `ps aux | grep python`
- Ask Manager to check interface contracts

### "Interface doesn't match"
- Read `docs/API-CONTRACTS.md`
- File request in `docs/INTERFACE-REQUESTS.md`
- Wait for Manager approval

### "Service won't start"
- Check logs: `cat logs/<service>.log`
- Run health check: `make check-health`
- Ask Ops dev to investigate

---

## Quick Reference

| Window | Branch | Command | Port/Output |
|--------|--------|---------|-------------|
| Manager | `main` | Monitor | - |
| Backend | `backend/initial` | `make backend` | :8000 |
| RAG | `rag/initial` | `make rag` | logs/rag.log |
| LaTeX | `latex/initial` | `make latex` | latex/output/*.pdf |
| Frontend | `frontend/initial` | (Backend serves) | :8000 |
| Ops | `ops/initial` | `make check-health` | - |
