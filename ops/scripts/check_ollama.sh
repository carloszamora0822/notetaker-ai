#!/bin/bash
echo "🔍 Checking Ollama Service..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running"
    echo "Start with: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# List models
echo ""
echo "📦 Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[] | "  - \(.name) (\(.size / 1000000000 | floor)GB)"'

# Test the model used in app
echo ""
echo "🧪 Testing model 'llama3.2:3b'..."
RESPONSE=$(curl -s -X POST http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [{"role": "user", "content": "Say hello"}],
  "stream": false
}')

if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ Model test failed:"
    echo "$RESPONSE" | jq -r '.error'
    echo ""
    echo "💡 Available models are listed above."
    echo "💡 Update rag/llm_client.py with correct model name."
    exit 1
else
    echo "✅ Model 'llama3.2:3b' works correctly"
fi

echo ""
echo "🎯 Recommended models:"
echo "  - llama3.2:3b (2GB) - Good balance ⭐"
echo "  - llama3:latest (4.6GB) - Best quality"
echo "  - phi3:latest (2GB) - Fastest"
echo "  - mistral:latest (4.3GB) - Alternative"
