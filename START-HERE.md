# 🚀 START HERE - Multi-Developer Setup Guide

**You are ready to run the multi-IDE development environment!**

---

## ✅ What's Been Set Up

### Core Documentation
- ✅ `MASTER-PROMPT.md` - Project architecture overview
- ✅ `README.md` - Quick start guide
- ✅ `docs/API-CONTRACTS.md` - **THE LAW** - interface specifications
- ✅ `docs/MANAGER-GUIDE.md` - **YOUR GUIDE** - coordination rules
- ✅ `docs/WINDOW-SETUP.md` - How to open IDE windows
- ✅ `docs/SPRINT-TRACKER.md` - Task tracking
- ✅ `docs/INTERFACE-REQUESTS.md` - Request interface changes

### Role-Specific Guides
- ✅ `backend/README-DEV.md` - Backend developer guide
- ✅ `rag/README-DEV.md` - RAG developer guide
- ✅ `latex/README-DEV.md` - LaTeX developer guide
- ✅ `frontend/README-DEV.md` - Frontend developer guide
- ✅ `ops/README-DEV.md` - Ops developer guide

### Infrastructure
- ✅ Directory structure created
- ✅ Makefile with all targets
- ✅ Pre-commit hooks configured
- ✅ Git repository initialized
- ✅ Operational scripts (health checks, bootstrap)
- ✅ LaTeX watcher script
- ✅ tmux workspace script

---

## 🎯 Your Next Steps

### Step 1: Bootstrap the Environment (5 minutes)

```bash
cd /Users/carloszamora/Desktop/notetaker-ai

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
make bootstrap

# Check everything is working
make check-interfaces
```

### Step 2: Download Embedding Model (one-time, ~500MB)

```bash
# Option A: Using Python
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
model.save('rag/models/bge-small-en-v1.5')
print("✓ Model downloaded to rag/models/bge-small-en-v1.5/")
EOF

# Option B: Manual download
# Visit: https://huggingface.co/BAAI/bge-small-en-v1.5
# Download and extract to: rag/models/bge-small-en-v1.5/
```

### Step 3: Open Multiple IDE Windows

**YOU HAVE TWO OPTIONS:**

#### Option A: Automated (Recommended)
```bash
# Run this script to open 6 terminal windows automatically
osascript << 'EOF'
tell application "Terminal"
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat backend/README-DEV.md"
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat rag/README-DEV.md"
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat latex/README-DEV.md"
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat frontend/README-DEV.md"
  do script "cd /Users/carloszamora/Desktop/notetaker-ai && source .venv/bin/activate && cat ops/README-DEV.md"
end tell
EOF
```

#### Option B: Manual
Open your IDE (VSCode/Cursor/etc) and create 6 workspace folders:

1. **Manager Window** (Full repo)
   - Path: `/Users/carloszamora/Desktop/notetaker-ai`
   - Read: `docs/MANAGER-GUIDE.md`

2. **Backend Window**
   - Path: `/Users/carloszamora/Desktop/notetaker-ai/backend`
   - Read: `backend/README-DEV.md`

3. **RAG Window**
   - Path: `/Users/carloszamora/Desktop/notetaker-ai/rag`
   - Read: `rag/README-DEV.md`

4. **LaTeX Window**
   - Path: `/Users/carloszamora/Desktop/notetaker-ai/latex`
   - Read: `latex/README-DEV.md`

5. **Frontend Window**
   - Path: `/Users/carloszamora/Desktop/notetaker-ai/frontend`
   - Read: `frontend/README-DEV.md`

6. **Ops Window**
   - Path: `/Users/carloszamora/Desktop/notetaker-ai/ops`
   - Read: `ops/README-DEV.md`

---

## 📋 Your Role as Manager

### 1. Read Your Guide
```bash
cat docs/MANAGER-GUIDE.md
```

### 2. Enforce These Rules

**CRITICAL RULES YOU MUST ENFORCE:**

🚨 **NO CROSS-BOUNDARY IMPORTS**
- Backend can ONLY import from `rag.search` (documented functions)
- NO other direct imports between areas
- Use file-based communication (LaTeX queue) or HTTP (Frontend)

🚨 **NO HALLUCINATION**
- If a dev says "I'll call this function..." → STOP THEM
- Check `docs/API-CONTRACTS.md` first
- If it doesn't exist, use `docs/INTERFACE-REQUESTS.md`

🚨 **SINGLE SOURCE OF TRUTH**
- `config/app.yaml` - ONLY Ops edits, everyone reads
- `docs/API-CONTRACTS.md` - YOU maintain with Ops
- Status files - Each service writes its own, others read

### 3. Monitor These Files

```bash
# Status files (update every 30s when services run)
watch -n 5 'cat logs/*_status.json | jq .'

# Service logs
tail -f logs/*.log

# Interface requests
watch -n 30 'cat docs/INTERFACE-REQUESTS.md'

# Sprint progress
cat docs/SPRINT-TRACKER.md
```

### 4. Daily Manager Commands

```bash
# Morning check
make check-health
make check-interfaces

# During development
tail -f logs/*.log

# Before any merge
make check
python ops/scripts/check_interfaces.py

# Review sprint status
cat docs/SPRINT-TRACKER.md
```

---

## 🎬 Starting Development

### For Single-Person Multi-Instance Development

Each IDE window represents a specialized AI developer with LIMITED scope:

**Window 1: YOU (Manager)**
- Monitors all
- Enforces contracts
- Coordinates interfaces
- Merges work

**Windows 2-6: Specialized Developers**
- Each sees ONLY their folder
- Follows ONLY their README-DEV.md
- Cannot modify other areas
- Must use documented interfaces

### Test the Setup

```bash
# From Manager window
make dev
```

This should open 5 tmux panes:
1. Backend (FastAPI server)
2. RAG (Indexer)
3. LaTeX (Watcher)
4. UI (Browser shortcut)
5. Logs (Tail all logs)

---

## 📊 Sprint 0 Goals (2-4 hours total)

### Success Criteria

Each specialized developer should achieve:

**Backend** ✅
- [ ] `/health` endpoint works
- [ ] `/ingest` saves files
- [ ] Status file updates

**RAG** ✅
- [ ] Model loads successfully
- [ ] Status file updates
- [ ] Prints "[OK] Model loaded"

**LaTeX** ✅
- [ ] Compiles `default.tex` to PDF
- [ ] Watcher runs continuously
- [ ] Status file updates

**Frontend** ✅
- [ ] Templates render
- [ ] Forms POST to backend
- [ ] Basic CSS applied

**Ops** ✅
- [ ] `make bootstrap` works
- [ ] Health checks pass
- [ ] Documentation complete

### Integration Test

```bash
# Should succeed
curl http://localhost:8000/health

# Should save file
curl -F file=@test.txt -F class_code=TEST http://localhost:8000/ingest

# Should return PDF
ls latex/output/*.pdf
```

---

## 🆘 Troubleshooting

### "make bootstrap fails"
```bash
bash ops/scripts/bootstrap_mac.sh
# Then retry: make bootstrap
```

### "RAG model missing"
```bash
# Quick download
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5').save('rag/models/bge-small-en-v1.5')"
```

### "LaTeX won't compile"
```bash
brew install --cask basictex
# Restart terminal
```

### "Services won't start"
```bash
make check-health
cat logs/*.log
```

### "Interface confusion"
```bash
cat docs/API-CONTRACTS.md
# This is the ONLY source of truth for interfaces
```

---

## 📚 Quick Reference

| Command | Purpose |
|---------|---------|
| `make bootstrap` | Install dependencies |
| `make dev` | Start all services (tmux) |
| `make backend` | Run backend only |
| `make rag` | Run RAG only |
| `make latex` | Run LaTeX watcher only |
| `make check-health` | Check all services |
| `make check-interfaces` | Validate contracts |
| `make check` | Full quality check |
| `make help` | Show all targets |

---

## 🎯 You Are Ready!

**Everything is set up. Next actions:**

1. ✅ Run `make bootstrap`
2. ✅ Download embedding model
3. ✅ Open multiple IDE windows (or use AI instances with folder restrictions)
4. ✅ Each "developer" reads their `README-DEV.md`
5. ✅ YOU read `docs/MANAGER-GUIDE.md`
6. ✅ Everyone reads `docs/API-CONTRACTS.md`
7. ✅ Run `make dev` to start
8. ✅ Begin Sprint 0 tasks

---

## 💡 Pro Tips

- **Communication**: Use `docs/INTERFACE-REQUESTS.md` for new interfaces
- **Status**: Check `logs/*_status.json` for service health
- **Conflicts**: Refer to `docs/API-CONTRACTS.md` - it's the law
- **Progress**: Update `docs/SPRINT-TRACKER.md` daily
- **Quality**: Run `make check` before merging

**Good luck! You have a fully coordinated multi-developer system ready to go.**
