.PHONY: bootstrap dev backend rag latex ui clean test help check-health check-status check-interfaces fmt lint

# Default Python version
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Initial setup - create venv and install dependencies
	@echo "🔧 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "📦 Installing dependencies..."
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install fastapi uvicorn jinja2 python-multipart aiofiles
	$(BIN)/pip install langchain openai chromadb
	$(BIN)/pip install black flake8 isort pre-commit pytest
	@echo "✅ Bootstrap complete! Run 'source .venv/bin/activate'"

dev: ## Start all services using tmux
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make bootstrap' first."; \
		exit 1; \
	fi
	@echo "🚀 Starting development environment..."
	./ops/scripts/devmux.sh

backend: ## Run backend service
	@echo "🔥 Starting FastAPI backend..."
	@mkdir -p logs
	$(BIN)/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee logs/backend.log

rag: ## Run RAG service
	@echo "🧠 Starting RAG service..."
	@mkdir -p logs
	$(BIN)/python -m rag.service 2>&1 | tee logs/rag.log

latex: ## Watch and compile LaTeX files
	@echo "📝 Starting LaTeX compiler..."
	@mkdir -p latex/templates
	./latex/scripts/compile_watch.sh

ui: ## Serve frontend (for now, backend serves it)
	@echo "🎨 Frontend is served by backend on http://localhost:8000"
	@echo "Run 'make backend' if not already running"

clean: ## Clean generated files and caches
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf logs/*.log 2>/dev/null || true
	@echo "✨ Clean complete!"

test: ## Run tests
	@echo "🧪 Running tests..."
	$(BIN)/pytest tests/ -v

check-health: ## Check health of all services
	@bash ops/scripts/check_health.sh

check-status: ## Show status of all services
	@echo "==> Service Status"
	@echo "Backend:" && cat logs/backend_status.json 2>/dev/null | jq '.' || echo "Not running"
	@echo "RAG:" && cat logs/rag_status.json 2>/dev/null | jq '.' || echo "Not running"
	@echo "LaTeX:" && cat logs/latex_status.json 2>/dev/null | jq '.' || echo "Not running"

check-interfaces: ## Validate all interface contracts
	@python3 ops/scripts/check_interfaces.py

fmt: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	$(BIN)/black backend rag ops
	$(BIN)/isort backend rag ops

lint: ## Lint code with ruff
	@echo "🔍 Linting code..."
	$(BIN)/ruff check backend rag ops || true

check: fmt lint test check-interfaces ## Run all quality checks
	@echo "✅ All checks complete"

install-latex: ## Install LaTeX dependencies (macOS)
	@echo "📚 Installing LaTeX..."
	@if ! command -v latexmk >/dev/null 2>&1; then \
		echo "Installing BasicTeX via Homebrew..."; \
		brew install --cask basictex; \
		echo "⚠️  You may need to restart your terminal after installation"; \
	else \
		echo "✅ LaTeX already installed"; \
	fi
