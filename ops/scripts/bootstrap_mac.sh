#!/usr/bin/env bash
# Bootstrap notetaker-ai on macOS

set -euo pipefail

echo "==> notetaker-ai macOS Bootstrap"
echo ""

# Check Homebrew
if ! command -v brew &>/dev/null; then
  echo "❌ Homebrew not found"
  echo "Install from: https://brew.sh"
  exit 1
else
  echo "✓ Homebrew installed"
fi

# Check Python 3.11+
echo ""
echo "Checking Python..."
if python3 --version | grep -qE '3\.(1[1-9]|[2-9][0-9])'; then
  echo "✓ Python $(python3 --version) installed"
else
  echo "⚠️  Python 3.11+ not found, installing..."
  brew install python@3.11
fi

# Check LaTeX
echo ""
echo "Checking LaTeX..."
if command -v latexmk &>/dev/null; then
  echo "✓ latexmk installed"
else
  echo "⚠️  latexmk not found, installing BasicTeX..."
  brew install --cask basictex
  echo "⚠️  You may need to restart your terminal after BasicTeX installation"
fi

# Check tmux
echo ""
echo "Checking tmux..."
if command -v tmux &>/dev/null; then
  echo "✓ tmux installed"
else
  echo "⚠️  tmux not found, installing..."
  brew install tmux
fi

# Check jq
echo ""
echo "Checking jq..."
if command -v jq &>/dev/null; then
  echo "✓ jq installed"
else
  echo "⚠️  jq not found, installing..."
  brew install jq
fi

echo ""
echo "==> Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Restart your terminal (if BasicTeX was installed)"
echo "  2. cd $(pwd)"
echo "  3. source .venv/bin/activate"
echo "  4. make bootstrap"
echo "  5. Download embedding model to rag/models/bge-small-en-v1.5/"
echo "  6. make dev"
