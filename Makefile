# Variables
VENV = .venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python3

.PHONY: help dev start stop

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start backend in development mode
	@echo "🔧 Starting backend server..."
	@mkdir -p logs
	$(PYTHON) -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

install-latex: ## Install LaTeX dependencies (macOS)
	@echo "📚 Installing LaTeX..."
	@if ! command -v latexmk >/dev/null 2>&1; then \
		echo "Installing BasicTeX via Homebrew..."; \
		brew install --cask basictex; \
		echo "⚠️  You may need to restart your terminal after installation"; \
	else \
		echo "✅ LaTeX already installed"; \
	fi

# Note: start target is defined later in file (uses start.sh)

# Note: stop target is defined later in file with improved functionality

restart: stop start ## Restart all services

status: ## Show status of all running services
	@echo "📊 Service Status"
	@echo "================="
	@if lsof -ti:8000 >/dev/null 2>&1; then \
		echo "✅ Backend: Running on http://localhost:8000"; \
		curl -s http://localhost:8000/health | jq '.' 2>/dev/null || echo "  (health check failed)"; \
	else \
		echo "❌ Backend: Not running"; \
	fi
	@echo ""
	@if [ -f logs/rag_status.json ]; then \
		echo "🧠 RAG Status:"; \
		cat logs/rag_status.json | jq '{model_loaded, index_size, ready}' 2>/dev/null; \
	else \
		echo "⚠️  RAG: No status file"; \
	fi
	@echo ""
	@if [ -f logs/backend_status.json ]; then \
		echo "🔧 Backend Status:"; \
		cat logs/backend_status.json | jq '.' 2>/dev/null; \
	fi

quick-test: ## Quick test after startup
	@echo "🧪 Running quick integration test..."
	@echo "Creating test file..."
	@echo "This is a test note about artificial intelligence and machine learning" > /tmp/test_note.txt
	@echo ""
	@echo "1️⃣  Testing upload..."
	@curl -s -F "file=@/tmp/test_note.txt" -F "class_code=TEST" http://localhost:8000/ingest | jq '.'
	@sleep 2
	@echo ""
	@echo "2️⃣  Testing search..."
	@curl -s -X POST http://localhost:8000/rag/query \
		-H "Content-Type: application/json" \
		-d '{"q":"artificial intelligence","scope":"all"}' | jq '.'
	@rm -f /tmp/test_note.txt
	@echo ""
	@echo "✅ Quick test complete!"

db-health: ## Check vector database health
	@echo "🏥 Checking Vector Database Health..."
	@curl -s http://localhost:8000/api/health/vectordb | jq '.' || echo "❌ Backend not running"

db-cleanup: ## Clean up orphaned vectors
	@echo "🧹 Cleaning up orphaned vectors..."
	$(PYTHON) ops/scripts/cleanup_orphans.py

db-sync: db-cleanup ## Alias for db-cleanup (sync vector DB with filesystem)

start: ## Start everything (Ollama + Backend + Browser)
	@bash start.sh

stop: ## Stop all services (kills everything)
	@echo "🛑 Stopping Notetaker AI..."
	@echo ""
	@echo "Killing processes:"
	@pkill -9 -f "uvicorn backend.main" && echo "  ✓ Backend server killed" || echo "  - Backend not running"
	@pkill -9 -f "ollama serve" && echo "  ✓ Ollama killed" || echo "  - Ollama not running"
	@pkill -9 -f "ollama" && echo "  ✓ Any other Ollama processes killed" || true
	@lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  ✓ Port 8000 freed" || true
	@lsof -ti:11434 | xargs kill -9 2>/dev/null && echo "  ✓ Port 11434 freed (Ollama)" || true
	@echo ""
	@echo "✅ Everything stopped - All processes killed!"
	@echo "💾 RAM freed: ~500MB"
	@echo "💡 Restart with: make start"

restart: stop start ## Restart everything

ps: ## Show what's running (check for background processes)
	@echo "🔍 Checking for running processes..."
	@echo ""
	@pgrep -fl "uvicorn|ollama" || echo "✅ No background processes found"
	@echo ""
	@echo "Port 8000 (Backend):"
	@lsof -ti:8000 && echo "  ⚠️  Port 8000 is in use" || echo "  ✅ Port 8000 is free"
	@echo "Port 11434 (Ollama):"
	@lsof -ti:11434 && echo "  ⚠️  Port 11434 is in use" || echo "  ✅ Port 11434 is free"

clean: stop ## Nuclear option - kill everything and clean up
	@echo "💣 Nuclear cleanup..."
	@pkill -9 -f "uvicorn" 2>/dev/null || true
	@pkill -9 -f "ollama" 2>/dev/null || true
	@pkill -9 -f "python.*backend" 2>/dev/null || true
	@killall -9 ollama 2>/dev/null || true
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:11434 | xargs kill -9 2>/dev/null || true
	@echo "✅ Nuclear cleanup complete - nothing left running!"

check-ollama: ## Check Ollama service and models
	@bash ops/scripts/check_ollama.sh

fix-ollama: ## Install recommended model (llama3.2:3b)
	@echo "📦 Installing llama3.2:3b (recommended)..."
	ollama pull llama3.2:3b
	@echo "✅ Model installed!"
	@echo "💡 Run 'make check-ollama' to verify"

migrate-titles: ## Migrate files to AI-generated titles (DRY RUN first)
	@echo "🔍 Running migration preview..."
	$(BIN)/python ops/scripts/migrate_filenames.py --dry-run
	@echo ""
	@echo "💡 Review the changes above. If OK, run:"
	@echo "   make migrate-titles-apply"

migrate-titles-apply: ## Apply migration (DESTRUCTIVE)
	@echo "⚠️  This will rename files!"
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(BIN)/python ops/scripts/migrate_filenames.py

rollback-migration: ## Rollback migration (manual process)
	@echo "⚠️  Migration rollback requires manual intervention"
	@echo ""
	@echo "Steps to rollback:"
	@echo "1. Restore files from backup (if created)"
	@echo "2. Or manually rename files back to YYYY-MM-DD_CLASS.txt format"
	@echo "3. Run: make db-cleanup to refresh vector DB"
	@echo ""
	@echo "💡 Tip: Always test with --dry-run first!"

test-title-gen: ## Test AI title generation
	@echo "🧪 Running title generation tests..."
	$(BIN)/python ops/scripts/test_title_generation.py
