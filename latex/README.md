# LaTeX Module - NoteTaker AI

This module handles PDF generation from lecture notes using LaTeX.

## Status

✅ **Sprint 0 Complete**: Infrastructure setup
✅ **Sprint 1 Complete**: Renderer and queue processing
⚠️ **Blocked**: LaTeX installation required

## Installation Required

Before the watcher can compile PDFs, you need to install LaTeX:

```bash
brew install --cask basictex
# Then restart your terminal
```

Verify installation:
```bash
which latexmk
latexmk -version
```

## Directory Structure

```
latex/
├── templates/          # LaTeX templates
│   ├── default.tex    # Default template for testing
│   └── *.tex          # Generated templates from JSON
├── scripts/
│   ├── render.py      # JSON → .tex converter
│   └── compile_watch.sh  # Queue watcher & compiler
├── queue/             # Input/output JSON files
│   ├── *_input.json   # Incoming jobs
│   └── *_result.json  # Compilation results
└── output/            # Generated PDFs
```

## How It Works

### 1. Input Processing
Backend places JSON files in `queue/` with format:
```json
{
  "summary": "Lecture content...",
  "metadata": {
    "class_code": "CS101",
    "date": "2025-09-30",
    "title": "Lecture Title"
  },
  "output_name": "CS101_2025-09-30"
}
```

### 2. Rendering
- `render.py` reads JSON and generates `.tex` file
- Escapes LaTeX special characters (`&`, `%`, `$`, `#`, `_`, etc.)
- Writes to `templates/{output_name}.tex`

### 3. Compilation
- `compile_watch.sh` monitors queue every 2 seconds
- Compiles `.tex` files using `latexmk -xelatex`
- Outputs PDF to `output/` directory

### 4. Result Notification
Success:
```json
{
  "success": true,
  "pdf_path": "latex/output/CS101_2025-09-30.pdf",
  "error": null,
  "compile_time_sec": 2.5
}
```

Error:
```json
{
  "success": false,
  "pdf_path": null,
  "error": "Compilation failed",
  "compile_time_sec": 0
}
```

## Usage

### Start the Watcher
```bash
make latex
```

Or manually:
```bash
cd latex
./scripts/compile_watch.sh
```

### Test with Sample Job
```bash
cat > latex/queue/test_input.json << 'EOF'
{
  "summary": "Test summary content",
  "metadata": {
    "class_code": "TEST",
    "date": "2025-09-30",
    "title": "Test Lecture"
  },
  "output_name": "test"
}
EOF

# Wait a few seconds, then check:
ls -la latex/output/test.pdf
cat latex/queue/test_result.json
```

### View Logs
```bash
tail -f ../logs/latex.log
cat ../logs/latex_status.json
```

## Testing Completed

✅ Renderer successfully converts JSON to .tex
✅ Special character escaping works correctly
✅ Logging system operational
✅ Queue directory monitoring ready
✅ Status file generation working
⚠️ PDF compilation pending LaTeX installation

## Features

- **Automatic Queue Processing**: Monitors `queue/` for new jobs
- **Special Character Escaping**: Safely handles `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`
- **Error Handling**: Graceful failure with detailed error messages
- **Logging**: All operations logged to `logs/latex.log`
- **Status Tracking**: Real-time status in `logs/latex_status.json`
- **Archive System**: Processed files moved to `processed_*` or `failed_*`

## Next Steps

1. **Install LaTeX** (see Installation Required above)
2. **Test PDF compilation** with default.tex:
   ```bash
   cd latex/templates
   latexmk -xelatex default.tex
   ```
3. **Start the watcher service**
4. **Integrate with Backend** module

## Troubleshooting

### Compilation Fails
```bash
# Check LaTeX logs
cat latex/templates/*.log | grep Error

# Test manually
cd latex/templates
xelatex test.tex
```

### Queue Not Processing
```bash
# Check if watcher is running
ps aux | grep compile_watch

# Verify permissions
chmod +x latex/scripts/compile_watch.sh
```

### Missing Packages
If LaTeX complains about missing packages:
```bash
sudo tlmgr install <package-name>
```

## Interface Contract

See `docs/API-CONTRACTS.md` for complete specification.

**Consumes**: `latex/queue/{timestamp}_{class}_input.json`
**Produces**: `latex/queue/{timestamp}_{class}_result.json`
**Outputs**: `latex/output/{output_name}.pdf`
**Status**: `logs/latex_status.json` (updated every 2s)

## Development

Before committing:
```bash
git add -A
git commit -m "feat(latex): your changes"
```

---

**Module Owner**: LaTeX Developer
**Last Updated**: 2025-09-30
**Version**: Sprint 1 Complete
