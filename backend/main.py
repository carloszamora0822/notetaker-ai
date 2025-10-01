"""FastAPI backend for notetaker-ai"""
import asyncio
import json
import logging
from datetime import date, datetime
from pathlib import Path

import yaml

# Setup logging
logger = logging.getLogger(__name__)
# Theme and LaTeX imports
import sys

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# RAG imports
from rag.search import index_document
from rag.search import search as rag_search
from rag.search import search_with_synthesis

sys.path.append(str(Path(__file__).resolve().parent.parent / "config"))
from theme_manager import (
    class_exists,
    decrement_file_count,
    delete_class,
    delete_theme,
    get_color_palette,
    get_theme,
    increment_file_count,
    load_themes,
    register_class,
    save_theme,
)

sys.path.append(str(Path(__file__).resolve().parent.parent / "latex"))
from generator import generate_themed_latex

# Initialize app
app = FastAPI(title="notetaker-ai", version="0.1.0")

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

# Load config
CONFIG_PATH = BASE_DIR / "config" / "app.yaml"
if CONFIG_PATH.exists():
    CFG = yaml.safe_load(CONFIG_PATH.read_text())
else:
    CFG = {"paths": {"inbox_global": "./inbox"}}  # Fallback

# Mount static files for CSS/JS (if directory exists)
static_dir = BASE_DIR / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global state for status tracking
request_counter = 0


# Helper functions for AI-generated filenames
def sanitize_filename(title: str) -> str:
    """Sanitize AI-generated title for safe filename (spaces allowed)"""
    # Remove invalid filename characters but keep spaces
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    sanitized = title
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "")
    # Trim and limit length
    sanitized = sanitized.strip()[:100]
    return sanitized if sanitized else "Untitled"


def get_unique_filename(inbox_path: Path, base_name: str) -> str:
    """Get unique filename by adding (2), (3), etc. if file exists"""
    filename = f"{base_name}.txt"
    file_path = inbox_path / filename

    if not file_path.exists():
        return filename

    # File exists, find unique counter
    counter = 2
    while True:
        filename = f"{base_name} ({counter}).txt"
        file_path = inbox_path / filename
        if not file_path.exists():
            return filename
        counter += 1


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/health")
def health():
    """Health check endpoint - Sprint 0"""
    return {"ok": True, "time": datetime.now().isoformat()}


@app.get("/api/health/ollama")
async def ollama_health():
    """Check if Ollama is available and list models"""
    import requests

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return {
                "status": "ok",
                "service": "running",
                "models": [
                    {"name": m["name"], "size": m.get("size", 0)} for m in models
                ],
                "count": len(models),
            }
        else:
            return {
                "status": "error",
                "service": "unreachable",
                "error": f"Status code: {response.status_code}",
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "service": "not_running",
            "error": "Cannot connect to Ollama. Start with: ollama serve",
            "fix": "Run 'ollama serve' in a separate terminal",
        }
    except Exception as e:
        return {"status": "error", "service": "unknown", "error": str(e)}


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Serve upload page"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Serve search page"""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/manager", response_class=HTMLResponse)
async def manager_page(request: Request):
    """Serve file manager UI"""
    return templates.TemplateResponse("manager.html", {"request": request})


@app.get("/theme-editor", response_class=HTMLResponse)
async def theme_editor_page(request: Request):
    """Theme customization UI"""
    return templates.TemplateResponse("theme_editor.html", {"request": request})


@app.get("/api/themes")
async def list_themes():
    """Get all class themes"""
    themes = load_themes()
    # Remove internal color_palette from response
    return {
        "themes": {k: v for k, v in themes.items() if k != "color_palette"},
        "color_palette": get_color_palette(),
    }


@app.get("/api/themes/{class_code}")
async def get_class_theme(class_code: str):
    """Get theme for specific class"""
    return {"theme": get_theme(class_code)}


@app.post("/api/themes/{class_code}")
async def update_theme(class_code: str, theme: dict):
    """Update class theme"""
    save_theme(class_code, theme)
    return {"success": True, "theme": theme}


@app.delete("/api/themes/{class_code}")
async def reset_theme(class_code: str):
    """Reset class to default theme"""
    delete_theme(class_code)
    return {"success": True, "message": "Reset to default"}


@app.get("/api/classes")
async def list_classes():
    """Get all registered classes with metadata (with accurate file counts)"""
    themes = load_themes()

    # Get actual file counts from filesystem
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    actual_counts = {}

    if inbox_path.exists():
        import json

        for f in inbox_path.glob("*.txt"):
            # Try to get class from metadata file
            meta_path = inbox_path / f"{f.stem}.meta.json"
            if meta_path.exists():
                try:
                    metadata = json.loads(meta_path.read_text())
                    class_code = metadata.get("class_code", "GENERAL")
                except:
                    # Fallback: parse old filename format
                    parts = f.stem.split("_", 1)
                    if len(parts) > 1 and parts[0].count("-") == 2:
                        class_code = parts[1]
                    else:
                        class_code = "GENERAL"
            else:
                # Fallback: parse old filename format
                parts = f.stem.split("_", 1)
                if len(parts) > 1 and parts[0].count("-") == 2:
                    class_code = parts[1]
                else:
                    class_code = "GENERAL"

            actual_counts[class_code] = actual_counts.get(class_code, 0) + 1

    classes = []
    for code, theme in themes.items():
        if code in ["default", "color_palette"]:
            continue

        file_count = actual_counts.get(code, 0)

        classes.append(
            {
                "code": code,
                "color": theme.get("primary_color", "#0B72B9"),
                "file_count": file_count,
                "created_at": theme.get("created_at", None),
            }
        )

    # Sort by creation date
    classes.sort(key=lambda x: x["created_at"] or "", reverse=True)
    return {"classes": classes}


@app.delete("/api/classes/{class_code}")
async def delete_class_endpoint(class_code: str):
    """Delete class (must have 0 files)"""
    import json

    # Count actual files for this class
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    actual_count = 0

    if inbox_path.exists():
        for f in inbox_path.glob("*.txt"):
            # Check metadata file
            meta_path = inbox_path / f"{f.stem}.meta.json"
            if meta_path.exists():
                try:
                    metadata = json.loads(meta_path.read_text())
                    if metadata.get("class_code") == class_code:
                        actual_count += 1
                except:
                    pass
            else:
                # Check old filename format
                parts = f.stem.split("_", 1)
                if len(parts) > 1 and parts[0].count("-") == 2:
                    if parts[1] == class_code:
                        actual_count += 1

    if actual_count > 0:
        raise HTTPException(
            400, f"Cannot delete {class_code}: has {actual_count} files"
        )

    delete_class(class_code)
    return {"success": True, "message": f"Deleted class {class_code}"}


@app.get("/api/v1/info")
async def info():
    """API information"""
    return {
        "name": "notetaker-ai",
        "version": "0.1.0",
        "description": "AI-powered note taking with RAG and LaTeX support",
    }


@app.get("/api/files")
async def list_files(class_code: str = None):
    """List all uploaded files with enhanced metadata"""
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    if not inbox_path.exists():
        return {"files": []}

    import json

    files = []
    for f in inbox_path.glob("*.txt"):
        # Try to load metadata from sidecar JSON file
        meta_path = inbox_path / f"{f.stem}.meta.json"
        metadata = {}

        if meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text())
            except Exception as e:
                logger.warning(f"Failed to read metadata for {f.name}: {e}")

        # Get values from metadata or fallback to parsing filename
        if metadata:
            file_class_code = metadata.get("class_code", "GENERAL")
            title = metadata.get("title", f.stem)
            upload_timestamp = metadata.get("upload_timestamp")
            content_date = metadata.get("content_date")
            original_filename = metadata.get("original_filename")
        else:
            # Backward compatibility: Parse old format "2025-10-01_CLASSNAME.txt"
            parts = f.stem.split("_", 1)
            if len(parts) > 1 and parts[0].count("-") == 2:
                file_class_code = parts[1]
                title = f.stem
            else:
                file_class_code = "GENERAL"
                title = f.stem
            upload_timestamp = None
            content_date = None
            original_filename = None

        # Filter by class if requested
        if class_code and file_class_code != class_code:
            continue

        # Get PDF status
        pdf = BASE_DIR / "latex/output" / f"{f.stem}.pdf"

        # Build file info with rich metadata
        file_info = {
            "filename": f.name,
            "title": title,
            "class_code": file_class_code,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
            "upload_timestamp": upload_timestamp,
            "content_date": content_date,
            "original_filename": original_filename,
            "has_pdf": pdf.exists(),
            "pdf_url": f"/pdf/{f.stem}.pdf" if pdf.exists() else None,
        }
        files.append(file_info)

    # Sort by content_date if available, else upload_timestamp, else modified time
    def sort_key(x):
        # Prefer content_date (when extracted from notes)
        if x.get("content_date"):
            return x["content_date"]
        # Then upload_timestamp
        if x.get("upload_timestamp"):
            return x["upload_timestamp"]
        # Finally fall back to file modified time
        from datetime import datetime

        return datetime.fromtimestamp(x["modified"]).isoformat()

    files.sort(key=sort_key, reverse=True)
    return {"files": files, "total": len(files)}


@app.get("/api/file/{filename}")
async def get_file(filename: str):
    """Get file content for viewing/editing"""
    file_path = BASE_DIR / CFG["paths"]["inbox_global"] / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")

    parts = file_path.stem.split("_", 1)
    return {
        "filename": filename,
        "content": file_path.read_text(),
        "date": parts[0],
        "class_code": parts[1] if len(parts) > 1 else "GENERAL",
    }


@app.post("/api/sync")
async def sync_database():
    """Sync vector DB with filesystem - remove orphaned vectors"""
    import subprocess

    logger.info("🔄 Starting database sync...")
    try:
        result = subprocess.run(
            [".venv/bin/python3", "ops/scripts/cleanup_orphans.py"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
        )
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Database synced",
                "output": result.stdout,
            }
        return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/file/{filename}")
async def delete_file(filename: str):
    """Delete file and all related data"""
    from rag.search import delete_document

    count = 0

    # 1. Delete text file
    txt = BASE_DIR / CFG["paths"]["inbox_global"] / filename
    if txt.exists():
        txt.unlink()
        count += 1

    # 2. Delete from RAG index (improved)
    if delete_document(filename):
        count += 1

    # 3. Delete LaTeX template
    tex = BASE_DIR / "latex/templates" / f"{Path(filename).stem}.tex"
    if tex.exists():
        tex.unlink()
        count += 1

    # 4. Delete PDF
    pdf = BASE_DIR / "latex/output" / f"{Path(filename).stem}.pdf"
    if pdf.exists():
        pdf.unlink()
        count += 1

    # 5. Decrement file count for class
    parts = filename.split("_", 1)
    if len(parts) > 1:
        class_code = parts[1].replace(".txt", "")
        decrement_file_count(class_code)

    return {"success": True, "deleted_count": count}


@app.get("/pdf/{filename}")
async def serve_pdf(filename: str):
    """Serve compiled PDF"""
    pdf = BASE_DIR / "latex/output" / filename
    if not pdf.exists():
        raise HTTPException(404, "PDF not found")
    return FileResponse(pdf, media_type="application/pdf")


@app.post("/ingest")
async def ingest(file: UploadFile, class_code: str = Form("")):
    """Ingest endpoint - AI-generated filenames with smart metadata"""
    global request_counter
    request_counter += 1

    # STEP 1: Read file content
    content = await file.read()
    text = content.decode("utf-8")
    original_filename = file.filename or "upload.txt"

    # Normalize class code to UPPERCASE
    class_code = class_code.strip().upper() or "GENERAL"

    # Auto-register class if new
    if not class_exists(class_code):
        register_class(class_code)
        logger.info(f"Auto-registered new class: {class_code}")

    increment_file_count(class_code)

    # STEP 2: Generate AI title from content
    logger.info(f"🤖 Generating AI title for uploaded content...")
    from rag.title_generator import generate_title

    ai_title = generate_title(text)
    logger.info(f"📝 Generated title: {ai_title}")

    # STEP 3: Extract date from content (optional)
    from rag.title_generator import extract_date_from_content

    content_date = extract_date_from_content(text)
    logger.info(f"📅 Extracted date: {content_date or 'None'}")

    # STEP 4: Sanitize title for filename
    safe_title = sanitize_filename(ai_title)

    # STEP 5: Get unique filename (handles duplicates)
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    inbox_path.mkdir(exist_ok=True)
    filename = get_unique_filename(inbox_path, safe_title)
    logger.info(f"💾 Final filename: {filename}")

    # STEP 6: Save file
    file_path = inbox_path / filename
    file_path.write_text(text)

    # STEP 7: Create enhanced metadata
    upload_timestamp = datetime.now().isoformat()
    metadata = {
        "title": ai_title,
        "filename": filename,
        "class_code": class_code,
        "upload_timestamp": upload_timestamp,
        "content_date": content_date,
        "original_filename": original_filename,
        "date": content_date
        or upload_timestamp.split("T")[0],  # Required by index_document
    }

    # Save metadata as sidecar JSON file
    import json

    meta_path = inbox_path / f"{file_path.stem}.meta.json"
    meta_path.write_text(json.dumps(metadata, indent=2))
    logger.info(f"💾 Saved metadata: {meta_path.name}")

    # Index with new metadata
    indexed = index_document(text, metadata)

    # ✨ STEP 1: Format text with LLM before PDF generation
    logger.info(f"📝 Starting LLM formatting for {filename}...")
    from rag.llm_client import summarize_for_pdf

    format_result = summarize_for_pdf(text)
    formatted_text = format_result["formatted_text"]
    llm_success = format_result["success"]

    if llm_success:
        logger.info(f"✅ LLM formatting successful!")
    else:
        logger.warning(f"⚠️ LLM formatting failed: {format_result['error']}")
        logger.info("Using original text for PDF")

    # ✨ STEP 2: Convert formatted text to LaTeX and compile PDF
    pdf_url = None
    try:
        import subprocess

        # Get theme for this class
        theme = get_theme(class_code)

        # Generate themed LaTeX with formatted content and AI title
        # is_formatted=True means content has markdown-style formatting from LLM
        logger.info(f"📄 Generating LaTeX (formatted={llm_success})...")

        # Use content_date if available, else upload date
        display_date = content_date or upload_timestamp.split("T")[0]

        # Generate LaTeX with AI title
        tex_content, pdf_filename = generate_themed_latex(
            content=formatted_text,
            class_code=class_code,  # Keep actual class code
            date=display_date,
            title=ai_title,  # Pass AI title as title parameter
            theme=theme,
            is_formatted=llm_success,
        )

        logger.info(f"📄 Generated LaTeX with filename: {pdf_filename}")

        # Save .tex file
        tex_path = BASE_DIR / "latex/templates" / f"{file_path.stem}.tex"
        tex_path.parent.mkdir(exist_ok=True, parents=True)
        tex_path.write_text(tex_content)

        # Compile to PDF
        output_dir = BASE_DIR / "latex/output"
        output_dir.mkdir(exist_ok=True, parents=True)

        result = subprocess.run(
            [
                "pdflatex",
                "-output-directory",
                str(output_dir),
                "-interaction=nonstopmode",
                str(tex_path),
            ],
            capture_output=True,
            timeout=15,
        )

        # Check if PDF was actually created (pdflatex might return non-zero on warnings)
        pdf_path = output_dir / f"{file_path.stem}.pdf"
        if pdf_path.exists():
            pdf_url = f"/pdf/{file_path.stem}.pdf"
            logger.info(f"✅ PDF generated: {pdf_url}")
        else:
            logger.error(f"LaTeX compilation failed (return code: {result.returncode})")
            logger.error(f"stderr: {result.stderr.decode()[:500]}")
            logger.error(f"stdout: {result.stdout.decode()[:500]}")

    except Exception as e:
        logger.warning(f"PDF generation failed: {e}")

    return {
        "success": True,
        "title": ai_title,
        "filename": filename,
        "stored": str(file_path),
        "class_code": class_code,
        "upload_timestamp": upload_timestamp,
        "content_date": content_date,
        "original_filename": original_filename,
        "indexed": indexed,
        "pdf_url": pdf_url,
        "llm_formatted": llm_success,
        "format_error": format_result.get("error"),
        "model_used": format_result.get("model_used"),
        "help": {
            "message": "LLM formatting failed. PDF uses basic formatting.",
            "action": "Check /api/health/ollama for Ollama status",
        }
        if not llm_success and format_result.get("error")
        else None,
    }


# Pydantic model for RAG query
class QueryRequest(BaseModel):
    q: str
    scope: str = "all"


@app.post("/rag/query")
async def rag_query(request: QueryRequest):
    """RAG query endpoint with LLM synthesis"""
    global request_counter
    request_counter += 1

    try:
        # Use synthesis instead of raw search
        result = search_with_synthesis(query=request.q, top_k=8, scope=request.scope)

        return {
            "answer": result["answer"],
            "citations": result["citations"],
            "synthesized": result.get("synthesized", False),
            "num_sources": len(result["citations"]),
        }

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {
            "answer": "Sorry, I encountered an error processing your query.",
            "citations": [],
            "synthesized": False,
            "error": str(e),
        }


@app.post("/rag/query/categorized")
async def rag_query_categorized(request: QueryRequest):
    """
    RAG query with results grouped by class and date
    """
    from rag.search import search_with_categories

    try:
        result = search_with_categories(query=request.q, top_k=8, scope=request.scope)

        # Also synthesize answer
        from rag.search import search_with_synthesis

        synthesis = search_with_synthesis(query=request.q, top_k=8, scope=request.scope)

        return {
            "answer": synthesis["answer"],
            "results": result["results"],
            "by_class": result["by_class"],
            "by_date": result["by_date"],
            "total": result["total"],
        }

    except Exception as e:
        logger.error(f"Categorized query failed: {e}")
        raise HTTPException(500, str(e))


# Background task to write status file every 30 seconds
async def update_status_file():
    """Background task that updates logs/backend_status.json every 30s"""
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    status_file = logs_dir / "backend_status.json"

    while True:
        status = {
            "server_running": True,
            "port": 8000,
            "requests_handled": request_counter,
            "timestamp": datetime.now().isoformat(),
        }
        status_file.write_text(json.dumps(status, indent=2))
        await asyncio.sleep(30)


@app.on_event("startup")
async def startup_event():
    """Initialize status file and start background task"""
    # Create initial status file
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    status_file = logs_dir / "backend_status.json"

    initial_status = {
        "server_running": True,
        "port": 8000,
        "requests_handled": 0,
        "timestamp": datetime.now().isoformat(),
    }
    status_file.write_text(json.dumps(initial_status, indent=2))

    # Start background task
    asyncio.create_task(update_status_file())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
