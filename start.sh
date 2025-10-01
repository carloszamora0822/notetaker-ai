#!/bin/bash
# One-command startup script for notetaker-ai

echo "🚀 Starting Notetaker AI..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is running
echo "📦 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama not running. Starting it...${NC}"
    echo ""
    echo "   Opening new terminal for Ollama..."

    # Start Ollama in a new terminal (macOS)
    osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"' && echo \"🤖 Ollama Service\" && echo \"\" && ollama serve"' > /dev/null 2>&1

    # Wait for Ollama to start
    echo "   Waiting for Ollama to start..."
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Ollama started!${NC}"
            break
        fi
        sleep 1
    done
else
    echo -e "${GREEN}✅ Ollama already running${NC}"
fi

echo ""

# Check if model is installed
echo "🔍 Checking for LLM model..."
MODEL_CHECK=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -q "llama3.2:3b" && echo "found" || echo "missing")

if [ "$MODEL_CHECK" = "missing" ]; then
    echo -e "${YELLOW}⚠️  Model not found. Installing llama3.2:3b...${NC}"
    echo "   This will take a few minutes..."
    ollama pull llama3.2:3b
    echo -e "${GREEN}✅ Model installed!${NC}"
else
    echo -e "${GREEN}✅ Model ready (llama3.2:3b)${NC}"
fi

echo ""

# Start backend server
echo "🔧 Starting backend server..."
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
    echo "   Kill it first with: make stop"
    echo ""
else
    # Start backend in new terminal
    PROJECT_DIR=$(pwd)
    osascript -e 'tell application "Terminal" to do script "cd '"$PROJECT_DIR"' && echo \"⚙️  Backend Server\" && echo \"\" && echo \"Starting backend...\" && '"$PROJECT_DIR"'/.venv/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"' > /dev/null 2>&1

    # Wait for backend to start
    echo "   Waiting for backend to start..."
    BACKEND_STARTED=false
    for i in {1..15}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Backend started!${NC}"
            BACKEND_STARTED=true
            break
        fi
        printf "."
        sleep 1
    done
    echo ""

    if [ "$BACKEND_STARTED" = false ]; then
        echo -e "${RED}   ❌ Backend failed to start${NC}"
        echo "   Check logs: tail -f logs/backend.log"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}🎉 Notetaker AI is ready!${NC}"
echo ""
echo "📍 URLs:"
echo "   • Upload:  http://localhost:8000/upload"
echo "   • Search:  http://localhost:8000/search"
echo "   • Manager: http://localhost:8000/manager"
echo ""
echo "🌐 Opening browser..."
sleep 2
open http://localhost:8000/upload

echo ""
echo "💡 Tips:"
echo "   • Upload notes at /upload"
echo "   • Search notes at /search"
echo "   • Manage files at /manager"
echo ""
echo "🛑 To stop everything: make stop"
