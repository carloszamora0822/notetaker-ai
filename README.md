# notetaker-ai

**Offline-first AI-powered note taking system with RAG and LaTeX output.**

---

## Quick Start

```bash
# 1. Setup
source .venv/bin/activate
make bootstrap

# 2. Place embedding model
# Download from: https://huggingface.co/BAAI/bge-small-en-v1.5
# Place in: rag/models/bge-small-en-v1.5/

# 3. Run all services
make dev
```

---

## Architecture

```
┌──────────┐     ┌─────────┐     ┌────────┐
│ Frontend │────►│ Backend │────►│  RAG   │
│  (HTML)  │     │ FastAPI │     │ Vector │
└──────────┘     └────┬────┘     └────────┘
                      │
                      ▼
                 ┌────────┐
                 │ LaTeX  │
                 │  PDF   │
                 └────────┘
```

See `MASTER-PROMPT.md` for full project structure.

---

## Multi-Developer Setup

**For coordinated development with multiple IDE instances:**

1. **Read**: `docs/WINDOW-SETUP.md` - How to open separate windows
2. **Manager reads**: `docs/MANAGER-GUIDE.md` - Coordination rules
3. **Each dev reads**: `<area>/README-DEV.md` - Role-specific guide
4. **ALL read**: `docs/API-CONTRACTS.md` - Interface specifications

---

## Development

### Individual Services
```bash
make backend  # FastAPI on :8000
make rag      # RAG indexer (background)
make latex    # LaTeX watcher
```

### All Services (tmux)
```bash
make dev      # Opens 5-pane workspace
```

### Quality Checks
```bash
make check    # Format, lint, test
make test     # Run pytest
make check-health  # Service health
```

---

## Project Structure

```
notetaker-ai/
├── backend/        # FastAPI app
│   └── app/main.py
├── rag/            # Vector store & search
│   ├── indexer.py
│   └── models/     # Local embedding model
├── latex/          # PDF generation
│   ├── templates/
│   └── scripts/
├── frontend/       # Jinja2 templates
│   ├── templates/
│   └── static/
├── ops/            # Tooling & scripts
│   └── scripts/
├── config/         # Configuration
│   └── app.yaml
├── docs/           # Documentation
└── logs/           # Service logs
```

---

## Configuration

Edit `config/app.yaml` (Ops role only):
- Model paths
- Chunk sizes
- LaTeX engine
- Paths

---

## Documentation

- **MASTER-PROMPT.md** - Project overview
- **docs/API-CONTRACTS.md** - Interface specifications
- **docs/MANAGER-GUIDE.md** - Multi-dev coordination
- **docs/WINDOW-SETUP.md** - IDE window setup
- **docs/SPRINT-TRACKER.md** - Current sprint status
- **<area>/README-DEV.md** - Role-specific guides

---

## Troubleshooting

### Backend won't start
```bash
lsof -ti:8000 | xargs kill -9
make backend
```

### RAG model missing
```bash
# Download: https://huggingface.co/BAAI/bge-small-en-v1.5
# Extract to: rag/models/bge-small-en-v1.5/
```

### LaTeX not compiling
```bash
brew install --cask basictex
# Restart terminal
```

### Check service health
```bash
make check-health
cat logs/*_status.json | jq '.'
```

---

## Contributing

See `CONTRIBUTING.md` for:
- Branch naming conventions
- Commit message format
- PR requirements
- Code ownership

---

## License

MIT
