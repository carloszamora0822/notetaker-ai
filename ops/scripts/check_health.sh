#!/usr/bin/env bash
# Health check for all notetaker-ai services

echo "==> Checking notetaker-ai health..."
echo ""

# Check Python
if command -v python3 &>/dev/null; then
  echo "✓ Python: $(python3 --version)"
else
  echo "❌ Python not found"
  exit 1
fi

# Check venv
if [ -d ".venv" ]; then
  echo "✓ Virtual environment: .venv exists"
else
  echo "❌ .venv missing - run 'make bootstrap'"
  exit 1
fi

# Check config
if [ -f "config/app.yaml" ]; then
  echo "✓ Configuration: config/app.yaml exists"
else
  echo "❌ config/app.yaml missing"
  exit 1
fi

echo ""
echo "==> Service Status"
echo ""

# Backend status
if [ -f "logs/backend_status.json" ]; then
  echo "Backend:"
  cat logs/backend_status.json | jq '.' 2>/dev/null || echo "  ⚠️  Invalid JSON"
else
  echo "Backend: ❌ Not running (logs/backend_status.json missing)"
fi

echo ""

# RAG status
if [ -f "logs/rag_status.json" ]; then
  echo "RAG:"
  cat logs/rag_status.json | jq '.' 2>/dev/null || echo "  ⚠️  Invalid JSON"
else
  echo "RAG: ❌ Not running (logs/rag_status.json missing)"
fi

echo ""

# LaTeX status
if [ -f "logs/latex_status.json" ]; then
  echo "LaTeX:"
  cat logs/latex_status.json | jq '.' 2>/dev/null || echo "  ⚠️  Invalid JSON"
else
  echo "LaTeX: ❌ Not running (logs/latex_status.json missing)"
fi

echo ""
echo "==> Port Check"
echo ""

# Check port 8000
if lsof -i :8000 >/dev/null 2>&1; then
  echo "✓ Backend listening on :8000"
else
  echo "❌ Port 8000 not open (backend not running)"
fi

echo ""
echo "==> Health check complete"
