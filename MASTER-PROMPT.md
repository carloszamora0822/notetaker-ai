# MASTER-PROMPT: notetaker-ai Project Structure

## Project Layout

```
notetaker-ai/
├─ backend/
│  ├─ app/main.py          # FastAPI app (ingest, rag proxy, health)
│  └─ cli/                 # future CLI commands
├─ rag/
│  ├─ index/               # vector store persistence
│  ├─ models/              # place local embedding model here
│  └─ indexer.py           # loader/chunker/embedding skeleton
├─ latex/
│  ├─ templates/default.tex # handout template
│  └─ scripts/compile_watch.sh # latexmk watcher
├─ frontend/
│  ├─ templates/base.html  # Jinja base
│  └─ static/{css,js}/
├─ ops/
│  └─ scripts/devmux.sh    # tmux workspace
├─ config/app.yaml         # single source of truth
├─ semesters/              # your class data lands here later
├─ tests/                  # pytest tests
├─ logs/
├─ .gitignore .editorconfig .gitattributes .pre-commit-config.yaml
├─ CODEOWNERS CONTRIBUTING.md Makefile
└─ README.md (add later)
```

## Architecture Overview

### Backend (`backend/`)
- **FastAPI application** serving as the main API gateway
- Endpoints for:
  - Document ingestion
  - RAG proxy (query interface)
  - Health checks
- Future CLI commands for offline operations

### RAG System (`rag/`)
- **Vector store** persistence in `index/`
- **Local embedding models** stored in `models/`
- **Indexer** handles document loading, chunking, and embedding

### LaTeX Generation (`latex/`)
- **Template system** for generating handouts
- **Watch script** for automatic compilation via latexmk
- Outputs formatted notes and study materials

### Frontend (`frontend/`)
- **Jinja2 templates** for server-side rendering
- **Static assets** (CSS/JS) for UI
- Minimal, functional interface

### Operations (`ops/`)
- **tmux workspace script** for multi-service development
- Orchestrates: backend, rag, latex compiler, UI, and logs

### Configuration
- **`config/app.yaml`** - Single source of truth for all configuration
- Environment-specific settings
- Model and service parameters

### Data
- **`semesters/`** - Organized class notes and materials
- **`logs/`** - Application and service logs
- **`tests/`** - Pytest test suite

## Development Workflow

1. Bootstrap: `make bootstrap`
2. Development: `make dev` (launches tmux workspace)
3. Individual services available via Makefile targets

## Quality Assurance
- Pre-commit hooks for code quality
- Black, flake8, isort for Python formatting
- Pytest for testing
