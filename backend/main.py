"""FastAPI backend for notetaker-ai"""
import asyncio
import json
import logging
from datetime import date, datetime
from pathlib import Path

import yaml

# Setup logging
logger = logging.getLogger(__name__)
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# RAG imports
from rag.search import index_document, search_with_synthesis
from rag.search import search as rag_search

# Theme and LaTeX imports
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "config"))
from theme_manager import (
    get_theme, save_theme, delete_theme, get_color_palette, load_themes,
    class_exists, register_class, increment_file_count, decrement_file_count, delete_class
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
                "models": [{"name": m["name"], "size": m.get("size", 0)} for m in models],
                "count": len(models)
            }
        else:
            return {
                "status": "error",
                "service": "unreachable",
                "error": f"Status code: {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "service": "not_running",
            "error": "Cannot connect to Ollama. Start with: ollama serve",
            "fix": "Run 'ollama serve' in a separate terminal"
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "unknown",
            "error": str(e)
        }


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
        "color_palette": get_color_palette()
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
    """Get all registered classes with metadata"""
    themes = load_themes()
    classes = []
    
    for code, theme in themes.items():
        if code in ['default', 'color_palette']:
            continue
        
        classes.append({
            "code": code,
            "color": theme.get('primary_color', '#0B72B9'),
            "file_count": theme.get('file_count', 0),
            "created_at": theme.get('created_at', None)
        })
    
    # Sort by creation date
    classes.sort(key=lambda x: x['created_at'] or '', reverse=True)
    return {"classes": classes}


@app.delete("/api/classes/{class_code}")
async def delete_class_endpoint(class_code: str):
    """Delete class (must have 0 files)"""
    theme = get_theme(class_code)
    
    if theme.get('file_count', 0) > 0:
        raise HTTPException(400, f"Cannot delete {class_code}: has {theme['file_count']} files")
    
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
    """List all uploaded files with metadata"""
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    if not inbox_path.exists():
        return {"files": []}
    
    files = []
    for f in inbox_path.glob("*.txt"):
        parts = f.stem.split("_", 1)
        fc = parts[1] if len(parts) > 1 else "GENERAL"
        if class_code and fc != class_code:
            continue
        
        pdf = BASE_DIR / "latex/output" / f"{f.stem}.pdf"
        files.append({
            "filename": f.name,
            "date": parts[0],
            "class_code": fc,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
            "has_pdf": pdf.exists(),
            "pdf_url": f"/pdf/{f.stem}.pdf" if pdf.exists() else None
        })
    
    files.sort(key=lambda x: x['modified'], reverse=True)
    return {"files": files}


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
        "class_code": parts[1] if len(parts) > 1 else "GENERAL"
    }


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
    parts = filename.split('_', 1)
    if len(parts) > 1:
        class_code = parts[1].replace('.txt', '')
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
    """Ingest endpoint - auto-registers classes and generates PDFs"""
    global request_counter
    request_counter += 1

    # Read file content
    content = await file.read()
    text = content.decode("utf-8")
    
    # Normalize class code to UPPERCASE
    class_code = class_code.strip().upper() or "GENERAL"
    
    # Auto-register class if new
    if not class_exists(class_code):
        register_class(class_code)
        logger.info(f"Auto-registered new class: {class_code}")
    
    # Increment file count
    increment_file_count(class_code)

    # Build filename
    today = date.today().isoformat()
    filename = f"{today}_{class_code}.txt"

    # Save to inbox (using config)
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    inbox_path.mkdir(exist_ok=True)

    file_path = inbox_path / filename
    file_path.write_text(text)

    receipt_id = f"{today}_{class_code}" if class_code else today

    # Index RAW text in RAG (for search)
    metadata = {
        "class_code": class_code,
        "date": today,
        "filename": filename,
    }

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
        
        # Generate themed LaTeX with formatted content
        # is_formatted=True means content has markdown-style formatting from LLM
        logger.info(f"📄 Generating LaTeX (formatted={llm_success})...")
        tex_content = generate_themed_latex(
            content=formatted_text,
            class_code=class_code,
            date=today,
            theme=theme,
            is_formatted=llm_success  # Only use markdown conversion if LLM succeeded
        )
        
        # Save .tex file
        tex_path = BASE_DIR / "latex/templates" / f"{file_path.stem}.tex"
        tex_path.parent.mkdir(exist_ok=True, parents=True)
        tex_path.write_text(tex_content)
        
        # Compile to PDF
        output_dir = BASE_DIR / "latex/output"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        result = subprocess.run(
            ["pdflatex", "-output-directory", str(output_dir), 
             "-interaction=nonstopmode", str(tex_path)],
            capture_output=True,
            timeout=15
        )
        
        if result.returncode == 0:
            pdf_url = f"/pdf/{file_path.stem}.pdf"
            logger.info(f"✅ PDF generated: {pdf_url}")
        else:
            logger.error(f"LaTeX compilation failed: {result.stderr.decode()}")
            
    except Exception as e:
        logger.warning(f"PDF generation failed: {e}")

    return {
        "stored": str(file_path),
        "receipt_id": f"{today}_{class_code}",
        "indexed": indexed,
        "pdf_url": pdf_url,
        "llm_formatted": llm_success,
        "format_error": format_result.get("error"),
        "model_used": format_result.get("model_used"),  # Show which model was used
        "help": {
            "message": "LLM formatting failed. PDF uses basic formatting.",
            "action": "Check /api/health/ollama for Ollama status"
        } if not llm_success and format_result.get("error") else None
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
        result = search_with_synthesis(
            query=request.q,
            top_k=8,
            scope=request.scope
        )
        
        return {
            "answer": result['answer'],
            "citations": result['citations'],
            "synthesized": result.get('synthesized', False),
            "num_sources": len(result['citations'])
        }
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {
            "answer": "Sorry, I encountered an error processing your query.",
            "citations": [],
            "synthesized": False,
            "error": str(e)
        }


@app.post("/rag/query/categorized")
async def rag_query_categorized(request: QueryRequest):
    """
    RAG query with results grouped by class and date
    """
    from rag.search import search_with_categories
    
    try:
        result = search_with_categories(
            query=request.q,
            top_k=8,
            scope=request.scope
        )
        
        # Also synthesize answer
        from rag.search import search_with_synthesis
        synthesis = search_with_synthesis(
            query=request.q,
            top_k=8,
            scope=request.scope
        )
        
        return {
            "answer": synthesis['answer'],
            "results": result['results'],
            "by_class": result['by_class'],
            "by_date": result['by_date'],
            "total": result['total']
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
