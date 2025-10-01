# LaTeX Developer Guide

**Your Role**: Template renderer, PDF compiler, watcher service.

---

## Your Workspace

```bash
cd /path/to/notetaker-ai/latex
```

**Files you OWN**:
- `latex/templates/*.tex` - LaTeX templates
- `latex/scripts/compile_watch.sh` - Watcher script
- `latex/scripts/render.py` - JSON → .tex renderer (Sprint 1)
- `latex/output/` - Generated PDFs
- `latex/queue/` - Input JSON files from Backend

**Files you READ** (do NOT edit):
- `config/app.yaml` - LaTeX engine, compile command

---

## Sprint 0 Tasks (2-4 hours)

### Task 1: Verify LaTeX installation
```bash
which latexmk
latexmk -version
```

If missing on macOS:
```bash
brew install --cask basictex
# Then restart terminal
```

### Task 2: Create default template
Already exists: `latex/templates/default.tex`

Test compile:
```bash
cd latex/templates
latexmk -xelatex -halt-on-error -interaction=nonstopmode default.tex
```

Should produce `default.pdf` without errors.

### Task 3: Implement watcher script
Already exists: `latex/scripts/compile_watch.sh`

Enhance to monitor queue:
```bash
#!/usr/bin/env bash
set -euo pipefail

QUEUE_DIR="../queue"
OUTPUT_DIR="../output"

mkdir -p "$QUEUE_DIR" "$OUTPUT_DIR"

while true; do
  # Compile templates
  cd templates
  for f in *.tex; do
    [ -f "$f" ] && latexmk -xelatex -halt-on-error -interaction=nonstopmode "$f" || true
  done
  cd ..

  # Process queue (Sprint 1)
  for input in "$QUEUE_DIR"/*_input.json; do
    [ -f "$input" ] && echo "Found job: $input" # TODO: call render.py
  done

  sleep 2
done
```

### Task 4: Write status file
```bash
# Add to watch script
cat > logs/latex_status.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "watcher_running": true,
  "queue_size": $(ls latex/queue/*_input.json 2>/dev/null | wc -l),
  "last_compile": {"file": "default.pdf", "success": true}
}
EOF
```

**Acceptance**:
- [ ] `make latex` starts watcher
- [ ] `default.tex` compiles to PDF successfully
- [ ] `logs/latex_status.json` exists
- [ ] Directories `latex/queue/` and `latex/output/` created

---

## Sprint 1 Tasks (4-8 hours)

### Task 1: Create Python renderer
```python
# latex/scripts/render.py
import json
import sys
from pathlib import Path
from datetime import datetime

TEMPLATE = r"""
\documentclass[11pt]{article}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{hyperref,xcolor,titlesec}

\definecolor{ClassColor}{HTML}{0B72B9}
\titleformat{\section}{\large\bfseries\color{ClassColor}}{}{0pt}{}

\begin{document}

\title{%TITLE%}
\date{%DATE%}
\maketitle

\section{Summary}
%SUMMARY%

\end{document}
"""

def escape_latex(text: str) -> str:
    """Escape LaTeX special characters"""
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def render(input_json: Path) -> Path:
    """Render JSON to .tex file"""
    data = json.loads(input_json.read_text())

    summary = escape_latex(data["summary"])
    metadata = data["metadata"]
    output_name = data["output_name"]

    tex_content = TEMPLATE.replace("%TITLE%", metadata.get("title", metadata["class_code"]))
    tex_content = tex_content.replace("%DATE%", metadata["date"])
    tex_content = tex_content.replace("%SUMMARY%", summary)

    tex_file = Path("latex/templates") / f"{output_name}.tex"
    tex_file.write_text(tex_content)

    return tex_file

if __name__ == "__main__":
    input_file = Path(sys.argv[1])
    tex_file = render(input_file)
    print(f"[OK] Rendered: {tex_file}")
```

### Task 2: Enhanced watcher with queue processing
```bash
#!/usr/bin/env bash
# latex/scripts/compile_watch.sh

process_queue() {
  for input in queue/*_input.json; do
    [ -f "$input" ] || continue

    echo "[LaTeX] Processing: $input"

    # Call renderer
    python scripts/render.py "$input"

    # Extract output name
    output_name=$(jq -r '.output_name' "$input")

    # Compile
    cd templates
    if latexmk -xelatex -halt-on-error -interaction=nonstopmode "${output_name}.tex"; then
      mv "${output_name}.pdf" ../output/

      # Write success result
      result_file="${input/_input.json/_result.json}"
      cat > "../$result_file" << EOF
{
  "success": true,
  "pdf_path": "latex/output/${output_name}.pdf",
  "error": null,
  "compile_time_sec": 2.5
}
EOF
    else
      # Write error result
      result_file="${input/_input.json/_result.json}"
      cat > "../$result_file" << EOF
{
  "success": false,
  "pdf_path": null,
  "error": "Compilation failed",
  "compile_time_sec": 0
}
EOF
    fi
    cd ..

    # Archive processed input
    mv "$input" "queue/processed_$(basename $input)"
  done
}

while true; do
  process_queue

  # Update status
  cat > logs/latex_status.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "watcher_running": true,
  "queue_size": $(ls queue/*_input.json 2>/dev/null | wc -l),
  "last_compile": {"file": "last.pdf", "success": true}
}
EOF

  sleep 2
done
```

### Task 3: Error handling and logging
```python
# Add to render.py
import logging

logging.basicConfig(
    filename='logs/latex.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def render(input_json: Path) -> Path:
    try:
        logging.info(f"Rendering {input_json}")
        # ... existing code ...
        logging.info(f"Success: {tex_file}")
        return tex_file
    except Exception as e:
        logging.error(f"Render failed: {e}")
        raise
```

**Acceptance**:
- [ ] Watcher monitors `latex/queue/` for `*_input.json`
- [ ] `render.py` converts JSON to .tex with escaped special chars
- [ ] Successful compile produces PDF in `latex/output/`
- [ ] Result JSON written to `latex/queue/*_result.json`
- [ ] Errors logged to `logs/latex.log`

---

## Interface Contract (READ-ONLY)

See `docs/API-CONTRACTS.md`. You MUST:

### Consume (file-based):
```json
// Input: latex/queue/{timestamp}_{class_code}_input.json
{
  "summary": "Text content...",
  "metadata": {
    "class_code": "CS101",
    "date": "2025-09-30",
    "title": "Lecture Title"
  },
  "output_name": "CS101_2025-09-30"
}
```

### Produce:
```json
// Output: latex/queue/{timestamp}_{class_code}_result.json
{
  "success": true,
  "pdf_path": "latex/output/CS101_2025-09-30.pdf",
  "error": null,
  "compile_time_sec": 2.5
}
```

### Status file:
```json
// logs/latex_status.json (update every 30s)
{
  "timestamp": "2025-09-30T23:00:00",
  "watcher_running": true,
  "queue_size": 2,
  "last_compile": {"file": "CS101.pdf", "success": true}
}
```

---

## Development Loop

```bash
# Start watcher
make latex

# In another terminal: test with sample job
cat > latex/queue/test_input.json << 'EOF'
{
  "summary": "Test summary content",
  "metadata": {"class_code": "TEST", "date": "2025-09-30", "title": "Test"},
  "output_name": "test"
}
EOF

# Wait a few seconds, check results
ls -la latex/output/test.pdf
cat latex/queue/test_result.json

# View logs
tail -f logs/latex.log

# Before commit
git add -A && git commit -m "feat(latex): <what you did>"
```

---

## Debugging

### Compilation fails?
```bash
# Check LaTeX log
cat latex/templates/*.log | grep Error

# Test manually
cd latex/templates
xelatex test.tex
```

### Special characters breaking?
Verify `escape_latex()` covers all cases:
- `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`

### Queue not processing?
```bash
# Check watcher is running
ps aux | grep compile_watch

# Check queue directory
ls -la latex/queue/

# Check permissions
chmod +x latex/scripts/compile_watch.sh
```

---

## Rules (DO NOT VIOLATE)

1. ✅ Read config from `config/app.yaml`
2. ✅ Monitor `latex/queue/` for input files
3. ✅ Write PDFs to `latex/output/`
4. ✅ Write result JSON back to `latex/queue/`
5. ✅ Update `logs/latex_status.json` every 30s
6. ✅ Escape ALL LaTeX special characters
7. ❌ Do NOT import Backend, RAG, or Frontend modules
8. ❌ Do NOT compile outside `latex/templates/` or `latex/output/`

---

## Need Help?

1. Check `docs/API-CONTRACTS.md` for file format spec
2. Test LaTeX manually first: `xelatex test.tex`
3. View logs: `tail -f logs/latex.log`
4. Ask Manager (main IDE instance)
