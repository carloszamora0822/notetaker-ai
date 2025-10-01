install-latex: ## Install LaTeX dependencies (macOS)
	@echo "📚 Installing LaTeX..."
	@if ! command -v latexmk >/dev/null 2>&1; then \
		echo "Installing BasicTeX via Homebrew..."; \
		brew install --cask basictex; \
		echo "⚠️  You may need to restart your terminal after installation"; \
	else \
		echo "✅ LaTeX already installed"; \
	fi

start: ## Start all services in background (one command!)
	@echo "🚀 Starting notetaker-ai..."
	@mkdir -p logs
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make bootstrap' first."; \
		exit 1; \
	fi
	@echo "Starting backend server..."
	@$(BIN)/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 & echo $$! > logs/backend.pid
	@sleep 3
	@if lsof -ti:8000 >/dev/null 2>&1; then \
		echo "✅ Backend started on http://localhost:8000"; \
	else \
		echo "❌ Backend failed to start. Check logs/backend.log"; \
		exit 1; \
	fi
	@echo ""
	@echo "🎉 System ready!"
	@echo "   📱 Open: http://localhost:8000/upload"
	@echo "   🔍 Search: http://localhost:8000/search"
	@echo "   📊 Status: make status"
	@echo "   🛑 Stop: make stop"

stop: ## Stop all running services
	@echo "🛑 Stopping services..."
	@if [ -f logs/backend.pid ]; then \
		kill $$(cat logs/backend.pid) 2>/dev/null && echo "✅ Backend stopped" || echo "⚠️  Backend not running"; \
		rm -f logs/backend.pid; \
	else \
		echo "⚠️  No backend PID file found"; \
	fi
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@echo "✅ All services stopped"

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
