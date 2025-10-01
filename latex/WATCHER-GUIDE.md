# LaTeX Watcher Service - Quick Start Guide

**Last Updated**: 2025-09-30 23:52:00
**Status**: Ready to Start (pending latexmk installation)

---

## Prerequisites

### Install latexmk

The watcher requires `latexmk` to compile LaTeX files. Install it using:

**Option 1: Using tlmgr** (Recommended)
```bash
sudo tlmgr install latexmk
```

**Option 2: Via Makefile**
```bash
make install-latex
# Then restart terminal
```

**Option 3: Manual BasicTeX reinstall**
```bash
brew reinstall --cask basictex
# Add to PATH if needed
export PATH="/Library/TeX/texbin:$PATH"
```

**Verify Installation**:
```bash
which latexmk
latexmk --version
```

Expected output:
```
/Library/TeX/texbin/latexmk
Latexmk, John Collins, ...
```

---

## Starting the Watcher

### Method 1: Using Makefile (Recommended)

From the project root:
```bash
make latex
```

This will:
1. Create necessary directories
2. Start the watcher script
3. Monitor `latex/queue/` for input files
4. Update `logs/latex_status.json` every 2 seconds

### Method 2: Direct Script Execution

```bash
cd /Users/carloszamora/Desktop/notetaker-ai
bash latex/scripts/compile_watch.sh
```

### Method 3: Background Process

To run the watcher in the background:
```bash
cd /Users/carloszamora/Desktop/notetaker-ai
nohup bash latex/scripts/compile_watch.sh > logs/latex_watcher.log 2>&1 &
echo $! > logs/latex_watcher.pid
```

Stop the background process:
```bash
kill $(cat logs/latex_watcher.pid)
rm logs/latex_watcher.pid
```

### Method 4: Using tmux (via devmux)

```bash
make dev  # Starts all services including LaTeX in tmux
```

---

## Testing the Watcher

### Step 1: Verify Watcher is Running

Check the logs:
```bash
tail -f logs/latex_status.json
```

Expected output (updates every 2 seconds):
```json
{
  "timestamp": "2025-09-30T23:52:00Z",
  "watcher_running": true,
  "queue_size": 0,
  "last_compile": {"file": "none", "success": true}
}
```

### Step 2: Test Manual Compilation

Before testing the full pipeline, verify LaTeX works:
```bash
cd latex/templates
latexmk -xelatex -halt-on-error -interaction=nonstopmode default.tex
ls -la default.pdf
```

Expected: `default.pdf` should be created without errors.

### Step 3: Test Queue Processing

Create a test job:
```bash
cat > latex/queue/test_$(date +%s)_input.json << 'EOF'
{
  "summary": "This is a test lecture about data structures. We cover arrays, linked lists, stacks, and queues.",
  "metadata": {
    "class_code": "CS102",
    "date": "2025-09-30",
    "title": "Data Structures Fundamentals"
  },
  "output_name": "CS102_test"
}
EOF
```

### Step 4: Monitor Processing

Watch the watcher logs:
```bash
# In one terminal
tail -f logs/latex.log

# In another terminal
watch -n 1 'ls -lh latex/output/'
```

Within 2-4 seconds, you should see:
1. Renderer processes the JSON
2. LaTeX compiles the .tex file
3. PDF appears in `latex/output/CS102_test.pdf`
4. Result JSON created: `latex/queue/test_*_result.json`

### Step 5: Verify Results

Check the result file:
```bash
cat latex/queue/test_*_result.json
```

Expected (success):
```json
{
  "success": true,
  "pdf_path": "latex/output/CS102_test.pdf",
  "error": null,
  "compile_time_sec": 2
}
```

Check the PDF:
```bash
open latex/output/CS102_test.pdf
```

---

## Watcher Behavior

### What It Does

1. **Monitors** `latex/queue/` every 2 seconds for `*_input.json` files
2. **Processes** each input file:
   - Calls `render.py` to generate `.tex` file
   - Compiles `.tex` to PDF using `latexmk -xelatex`
   - Moves PDF to `latex/output/`
   - Writes result JSON to `latex/queue/*_result.json`
3. **Archives** processed files:
   - Success: `latex/queue/processed_*.json`
   - Failure: `latex/queue/failed_*.json`
4. **Updates** `logs/latex_status.json` with current status

### Status File Format

```json
{
  "timestamp": "ISO-8601 UTC",
  "watcher_running": true,
  "queue_size": 0,
  "last_compile": {
    "file": "last_generated.pdf",
    "success": true
  }
}
```

### Log Files

- **`logs/latex.log`**: Detailed renderer logs
- **`logs/latex_status.json`**: Current watcher status
- **`logs/latex_watcher.log`**: Watcher script output (if using nohup)

---

## Troubleshooting

### Watcher Not Starting

**Check 1: Script Permissions**
```bash
ls -la latex/scripts/compile_watch.sh
# Should show: -rwxr-xr-x
chmod +x latex/scripts/compile_watch.sh
```

**Check 2: Dependencies**
```bash
which python3  # Should show Python 3
which latexmk  # Should show latexmk
```

**Check 3: Directory Structure**
```bash
ls -d latex/queue latex/output latex/templates
# All should exist
```

### Queue Not Processing

**Check 1: Watcher Running**
```bash
ps aux | grep compile_watch
```

**Check 2: File Naming**
Input files MUST end with `_input.json`:
```bash
# Correct
20250930_CS101_input.json

# Wrong (will be ignored)
20250930_CS101.json
input.json
```

**Check 3: JSON Format**
Validate your JSON:
```bash
cat latex/queue/your_input.json | python3 -m json.tool
```

### Compilation Fails

**Check 1: LaTeX Logs**
```bash
cat latex/templates/*.log | grep -i error
```

**Check 2: Special Characters**
The renderer escapes these automatically:
- `&` → `\&`
- `%` → `\%`
- `$` → `\$`
- `#` → `\#`
- `_` → `\_`
- `{`, `}`, `~`, `^`

**Check 3: Missing LaTeX Packages**
If compilation fails with "package not found":
```bash
sudo tlmgr install <package-name>
```

Common packages needed:
```bash
sudo tlmgr install xelatex xcolor titlesec fancyhdr parskip
```

---

## Integration with Backend

Once the watcher is running, the Backend can create lecture notes by:

1. **Dropping a JSON file** in `latex/queue/`:
```python
import json
from datetime import datetime

job_data = {
    "summary": lecture_summary,
    "metadata": {
        "class_code": "CS101",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": lecture_title
    },
    "output_name": f"CS101_{timestamp}"
}

with open(f"latex/queue/{timestamp}_CS101_input.json", "w") as f:
    json.dump(job_data, f)
```

2. **Polling for result** (or using file watcher):
```python
import time

result_file = f"latex/queue/{timestamp}_CS101_result.json"
for _ in range(30):  # Wait up to 60 seconds
    if os.path.exists(result_file):
        with open(result_file) as f:
            result = json.load(f)
            if result["success"]:
                pdf_path = result["pdf_path"]
                # Serve PDF to frontend
            break
    time.sleep(2)
```

---

## Performance Notes

- **Queue Check**: Every 2 seconds
- **Compilation Time**: ~2-5 seconds per document
- **Concurrent Jobs**: Processed sequentially (one at a time)
- **Memory Usage**: Low (~20MB for watcher, ~100MB during compilation)

---

## Quick Command Reference

```bash
# Start watcher
make latex

# Check status
cat logs/latex_status.json

# View logs
tail -f logs/latex.log

# List queue
ls -lh latex/queue/*_input.json

# List output PDFs
ls -lh latex/output/*.pdf

# Stop watcher (if background)
pkill -f compile_watch.sh

# Test compilation
cd latex/templates && latexmk -xelatex default.tex

# Clean up test files
rm latex/queue/processed_* latex/queue/failed_*
```

---

## Current Status

✅ Watcher script ready
✅ Status file writer implemented
✅ Renderer tested and working
✅ Makefile target configured
⏳ Waiting for latexmk installation

**Next Step**: Install latexmk, then run `make latex`
