# Ops Developer Guide

**Your Role**: Tooling, orchestration, quality gates, bootstrap scripts.

---

## Your Workspace

```bash
cd /path/to/notetaker-ai
```

**Files you OWN**:
- `ops/scripts/` - All operational scripts
- `config/app.yaml` - Configuration (others read-only)
- `Makefile` - Build automation
- `.pre-commit-config.yaml` - Git hooks
- `docs/` - Documentation (shared with Manager)

**Your Mission**: Keep everything running smoothly, prevent chaos.

---

## Sprint 0 Tasks (2-4 hours)

### Task 1: Verify bootstrap works
```bash
# Test on clean directory
cd /tmp && mkdir test-notetaker && cd test-notetaker
git clone /path/to/notetaker-ai .
source .venv/bin/activate
make bootstrap
```

Document any missing dependencies in `docs/SETUP.md`.

### Task 2: Create health check script
```bash
#!/usr/bin/env bash
# ops/scripts/check_health.sh

echo "==> Checking notetaker-ai health..."

# Check Python
python --version || { echo "❌ Python not found"; exit 1; }

# Check venv
[ -d ".venv" ] || { echo "❌ .venv missing - run 'make bootstrap'"; exit 1; }

# Check config
[ -f "config/app.yaml" ] || { echo "❌ config/app.yaml missing"; exit 1; }

# Check status files
echo "Backend status:"
cat logs/backend_status.json 2>/dev/null | jq '.' || echo "❌ Backend not running"

echo "RAG status:"
cat logs/rag_status.json 2>/dev/null | jq '.' || echo "❌ RAG not running"

echo "LaTeX status:"
cat logs/latex_status.json 2>/dev/null | jq '.' || echo "❌ LaTeX not running"

# Check ports
lsof -i :8000 >/dev/null && echo "✓ Backend listening on :8000" || echo "❌ Port 8000 not open"

echo "✓ Health check complete"
```

### Task 3: Create macOS bootstrap script
```bash
#!/usr/bin/env bash
# ops/scripts/bootstrap_mac.sh

set -euo pipefail

echo "==> notetaker-ai macOS Bootstrap"

# Check Homebrew
if ! command -v brew &>/dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check Python 3.11+
if ! python3 --version | grep -qE '3\.(11|12|13)'; then
  echo "Installing Python 3.11..."
  brew install python@3.11
fi

# Check LaTeX
if ! command -v latexmk &>/dev/null; then
  echo "Installing BasicTeX..."
  brew install --cask basictex
  echo "⚠️  You may need to restart your terminal"
fi

# Check tmux
if ! command -v tmux &>/dev/null; then
  echo "Installing tmux..."
  brew install tmux
fi

# Check jq
if ! command -v jq &>/dev/null; then
  echo "Installing jq..."
  brew install jq
fi

echo "✓ Bootstrap complete. Run 'make bootstrap' next."
```

### Task 4: Enhance Makefile with checks
```makefile
# Add to existing Makefile

.PHONY: check-health check-interfaces check-status

check-health:
	@bash ops/scripts/check_health.sh

check-interfaces:
	@echo "==> Checking interface contracts..."
	@python ops/scripts/check_interfaces.py

check-status:
	@echo "==> Service Status"
	@echo "Backend:" && cat logs/backend_status.json 2>/dev/null | jq '.' || echo "Not running"
	@echo "RAG:" && cat logs/rag_status.json 2>/dev/null | jq '.' || echo "Not running"
	@echo "LaTeX:" && cat logs/latex_status.json 2>/dev/null | jq '.' || echo "Not running"
```

**Acceptance**:
- [ ] `make bootstrap` completes on clean Mac
- [ ] `ops/scripts/check_health.sh` reports status of all services
- [ ] `ops/scripts/bootstrap_mac.sh` installs missing dependencies
- [ ] `make check-status` shows all service health

---

## Sprint 1 Tasks (4-8 hours)

### Task 1: Interface validation script
```python
# ops/scripts/check_interfaces.py
"""Validate that all interfaces match API contracts"""

import sys
from pathlib import Path
import importlib.util

def check_rag_interface():
    """Verify RAG exports required functions"""
    spec = importlib.util.spec_from_file_location("rag.search", "rag/search.py")
    if not spec:
        print("❌ rag/search.py not found")
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    required = ["search", "index_document", "get_status"]
    for func in required:
        if not hasattr(module, func):
            print(f"❌ rag.search missing: {func}()")
            return False

    print("✓ RAG interface valid")
    return True

def check_latex_queue():
    """Verify LaTeX directories exist"""
    required_dirs = [
        Path("latex/queue"),
        Path("latex/output"),
        Path("latex/templates")
    ]

    for d in required_dirs:
        if not d.exists():
            print(f"❌ Missing directory: {d}")
            return False

    print("✓ LaTeX directories valid")
    return True

def check_backend_endpoints():
    """Verify backend defines required endpoints"""
    backend_file = Path("backend/app/main.py")
    if not backend_file.exists():
        print("❌ backend/app/main.py not found")
        return False

    content = backend_file.read_text()
    required_endpoints = ["/health", "/ingest", "/rag/query"]

    for endpoint in required_endpoints:
        if endpoint not in content:
            print(f"❌ Backend missing endpoint: {endpoint}")
            return False

    print("✓ Backend endpoints valid")
    return True

if __name__ == "__main__":
    checks = [
        check_rag_interface,
        check_latex_queue,
        check_backend_endpoints
    ]

    results = [check() for check in checks]

    if all(results):
        print("\n✓ All interfaces valid")
        sys.exit(0)
    else:
        print("\n❌ Interface validation failed")
        sys.exit(1)
```

### Task 2: Automated testing setup
```python
# ops/scripts/run_integration_tests.py
"""Integration tests across components"""

import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test backend health endpoint"""
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["ok"] == True
    print("✓ Health check passed")

def test_ingest():
    """Test file upload"""
    files = {"file": ("test.txt", b"Test content", "text/plain")}
    data = {"class_code": "TEST"}

    resp = requests.post(f"{BASE_URL}/ingest", files=files, data=data)
    assert resp.status_code == 200
    assert "stored" in resp.json()
    print("✓ Ingest test passed")

def test_rag_query():
    """Test RAG search"""
    payload = {"q": "test query", "scope": "all"}
    resp = requests.post(f"{BASE_URL}/rag/query", json=payload)
    assert resp.status_code == 200
    assert "answer" in resp.json()
    print("✓ RAG query test passed")

def test_latex_pipeline():
    """Test LaTeX generation"""
    input_file = Path("latex/queue/test_input.json")
    input_file.write_text(json.dumps({
        "summary": "Test summary",
        "metadata": {"class_code": "TEST", "date": "2025-09-30", "title": "Test"},
        "output_name": "test"
    }))

    # Wait for processing
    time.sleep(5)

    result_file = Path("latex/queue/test_result.json")
    assert result_file.exists(), "LaTeX result not generated"

    result = json.loads(result_file.read_text())
    assert result["success"] == True
    print("✓ LaTeX pipeline test passed")

if __name__ == "__main__":
    tests = [test_health, test_ingest, test_rag_query, test_latex_pipeline]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            exit(1)

    print("\n✓ All integration tests passed")
```

### Task 3: Logging setup
```python
# ops/scripts/setup_logging.py
"""Configure logging for all services"""

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str, level=logging.INFO):
    """Create logger for a service"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    fh = logging.FileHandler(LOG_DIR / f"{name}.log")
    fh.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
```

### Task 4: Documentation
```markdown
<!-- docs/SETUP.md -->
# Setup Guide

## Prerequisites (macOS)

Run automated setup:
```bash
bash ops/scripts/bootstrap_mac.sh
```

Or manually install:
- Python 3.11+
- BasicTeX (for LaTeX compilation)
- tmux (for dev environment)
- jq (for JSON parsing)

## First Time Setup

1. Clone repository
2. Create virtual environment: `python3 -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `make bootstrap`
5. Place embedding model in `rag/models/bge-small-en-v1.5/`

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
# If missing: brew install --cask basictex
```

### RAG model missing
Download: https://huggingface.co/BAAI/bge-small-en-v1.5
Place in: `rag/models/bge-small-en-v1.5/`
```

**Acceptance**:
- [ ] `check_interfaces.py` validates all contracts
- [ ] `run_integration_tests.py` tests full pipeline
- [ ] Logging configured for all services
- [ ] `docs/SETUP.md` complete with troubleshooting

---

## Rules (DO NOT VIOLATE)

1. ✅ You are the ONLY one who edits `config/app.yaml`
2. ✅ Maintain `docs/API-CONTRACTS.md` with Manager
3. ✅ Run health checks before merging any PR
4. ✅ Keep Makefile targets up to date
5. ❌ Do NOT edit code in backend/, rag/, latex/, frontend/
6. ❌ Do NOT change interfaces without updating contracts

---

## Daily Ops Routine

### Morning
```bash
git pull
make check-health
make check-interfaces
```

### Before Merges
```bash
make check
make test
python ops/scripts/check_interfaces.py
```

### Monitoring
```bash
# Watch all logs
tail -f logs/*.log

# Status dashboard
watch -n 5 'make check-status'
```

---

## Need Help?

1. Check `docs/MANAGER-GUIDE.md` for coordination rules
2. Review service logs in `logs/`
3. Run health checks to identify issues
4. Coordinate with Manager (main IDE instance)
