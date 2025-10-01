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

Follow these steps to set up notetaker-ai from scratch:

### 1. Clone Repository

```bash
git clone <repository-url> notetaker-ai
cd notetaker-ai
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
make bootstrap
```

This will install all Python packages including:
- FastAPI & Uvicorn (backend)
- LangChain & ChromaDB (RAG)
- Black, Flake8, isort (code quality)
- pytest (testing)

### 4. Download Embedding Model

The RAG service requires the BGE embedding model:

```bash
# Create model directory
mkdir -p rag/models/bge-small-en-v1.5

# Download from Hugging Face
# Visit: https://huggingface.co/BAAI/bge-small-en-v1.5
# Or use git-lfs:
cd rag/models
git lfs install
git clone https://huggingface.co/BAAI/bge-small-en-v1.5
cd ../..
```

### 5. Verify Setup

Run health checks to verify everything is configured correctly:

```bash
make check-health
```

## Running the Application

### Start All Services

Use tmux to run all services in one command:

```bash
make dev
```

This starts:
- **Backend** on http://localhost:8000
- **RAG service** (background)
- **LaTeX watcher** (background)

To detach from tmux: `Ctrl+b` then `d`  
To reattach: `tmux attach -t notetaker-dev`

### Start Individual Services

You can also run services separately:

```bash
# Terminal 1: Backend
make backend

# Terminal 2: RAG service
make rag

# Terminal 3: LaTeX watcher
make latex
```

### Check Service Status

View the status of all running services:

```bash
make check-status
```

Or run a comprehensive health check:

```bash
make check-health
```

## Development Workflow

### Code Quality

Format and lint your code:

```bash
# Format with black and isort
make fmt

# Lint with ruff
make lint
```

### Running Tests

```bash
# Run unit tests
make test

# Run integration tests (requires services to be running)
python3 ops/scripts/run_integration_tests.py
```

### Check Interfaces

Verify all service interfaces are valid:

```bash
make check-interfaces
```

## Directory Structure

```
notetaker-ai/
├── backend/          # FastAPI backend service
├── rag/              # RAG search and indexing
├── latex/            # LaTeX compilation pipeline
│   ├── queue/        # Input JSON files
│   ├── output/       # Generated PDFs
│   └── templates/    # LaTeX templates
├── frontend/         # Web UI templates
├── inbox/            # Uploaded files staging
├── semesters/        # Organized class notes
├── logs/             # Service logs
├── config/           # Configuration files
│   └── app.yaml      # Main application config
├── ops/              # Operational scripts
│   └── scripts/      # Bootstrap, health checks, etc.
└── docs/             # Documentation
```

## Configuration

The main configuration file is `config/app.yaml`. It contains settings for:

- Backend server (host, port, CORS)
- RAG service (model path, chunk size, index location)
- LaTeX pipeline (directories, timeout)
- Logging configuration

**Note**: Only the OPS developer should edit `config/app.yaml`.

## Troubleshooting

### Port 8000 Already in Use

If the backend fails to start because port 8000 is in use:

```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or find what's using it
lsof -i:8000
```

### LaTeX Not Compiling

**Check if latexmk is installed**:
```bash
which latexmk
```

**If missing, install BasicTeX**:
```bash
brew install --cask basictex
# Restart your terminal
```

**Verify LaTeX installation**:
```bash
latexmk --version
```

**Check LaTeX logs**:
```bash
tail -f logs/latex.log
```

### RAG Model Missing

If you see errors about missing embedding model:

```bash
# Check if model directory exists
ls -la rag/models/bge-small-en-v1.5/

# Download model
cd rag/models
git lfs install
git clone https://huggingface.co/BAAI/bge-small-en-v1.5
```

### Virtual Environment Issues

**Recreate virtual environment**:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
make bootstrap
```

### Services Not Starting

**Check logs**:
```bash
# View all logs
ls -la logs/

# Tail specific service log
tail -f logs/backend.log
tail -f logs/rag.log
tail -f logs/latex.log
```

**Verify dependencies**:
```bash
source .venv/bin/activate
pip list
```

**Check service status**:
```bash
make check-status
```

### Permission Errors

**Make scripts executable**:
```bash
chmod +x ops/scripts/*.sh
chmod +x latex/scripts/*.sh
```

### ChromaDB Issues

If RAG service fails due to ChromaDB errors:

```bash
# Clear ChromaDB data
rm -rf rag/data/chroma_db

# Restart RAG service
make rag
```

## Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Start development environment
make dev

# Check service health
make check-health

# View service status
make check-status

# Format code
make fmt

# Run all checks (format, lint, test, interfaces)
make check

# Clean up generated files
make clean

# View available commands
make help
```

## Getting Help

1. **Check logs**: All services write to `logs/` directory
2. **Run health check**: `make check-health`
3. **Verify interfaces**: `make check-interfaces`
4. **Review documentation**:
   - `docs/API-CONTRACTS.md` - Interface specifications
   - `docs/MANAGER-GUIDE.md` - Project coordination
   - `ops/README-DEV.md` - OPS developer guide

## Next Steps

After setup:

1. ✅ Verify all services are running: `make check-status`
2. ✅ Open http://localhost:8000 in your browser
3. ✅ Upload a test document through the UI
4. ✅ Try searching with RAG
5. ✅ Generate a LaTeX PDF

For development coordination, see `docs/MANAGER-GUIDE.md`.
