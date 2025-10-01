#!/usr/bin/env bash
set -euo pipefail
cd latex/templates
while true; do
if ls *.tex >/dev/null 2>&1; then
for f in *.tex; do
echo "Compiling $f" && latexmk -xelatex -halt-on-error -interaction=nonstopmode "$f" || true
done
fi
sleep 2
done
