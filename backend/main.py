"""FastAPI backend for notetaker-ai"""
import asyncio
import json
import yaml
from datetime import datetime, date
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# RAG imports
from rag.search import search as rag_search, index_document

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


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Serve upload page"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Serve search page"""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/api/v1/info")
async def info():
    """API information"""
    return {
        "name": "notetaker-ai",
        "version": "0.1.0",
        "description": "AI-powered note taking with RAG and LaTeX support",
    }


@app.post("/ingest")
async def ingest(file: UploadFile, class_code: str = Form("")):
    """Ingest endpoint - saves and indexes documents"""
    global request_counter
    request_counter += 1
    
    # Read file content
    content = await file.read()
    text = content.decode("utf-8")
    
    # Build filename
    today = date.today().isoformat()
    filename = f"{today}_{class_code}.txt" if class_code else f"{today}.txt"
    
    # Save to inbox (using config)
    inbox_path = BASE_DIR / CFG["paths"]["inbox_global"]
    inbox_path.mkdir(exist_ok=True)
    
    file_path = inbox_path / filename
    file_path.write_text(text)
    
    receipt_id = f"{today}_{class_code}" if class_code else today
    
    # Index the document in RAG
    metadata = {
        "class_code": class_code or "GENERAL",
        "date": today,
        "filename": filename
    }
    
    indexed = index_document(text, metadata)
    
    return {
        "stored": str(file_path),
        "receipt_id": receipt_id,
        "indexed": indexed  # Add indexing status
    }


# Pydantic model for RAG query
class QueryRequest(BaseModel):
    q: str
    scope: str = "all"


@app.post("/rag/query")
async def rag_query(request: QueryRequest):
    """RAG query endpoint - searches indexed notes"""
    global request_counter
    request_counter += 1
    
    # Call RAG search
    results = rag_search(request.q, top_k=8, scope=request.scope)
    
    if not results:
        return {
            "answer": "No relevant notes found for your query.",
            "citations": []
        }
    
    # Generate answer from top results
    top_chunks = [r['chunk'] for r in results[:3]]
    answer = f"Found {len(results)} relevant notes. Here are the key points:\n\n"
    answer += "\n\n".join([f"• {chunk[:200]}..." for chunk in top_chunks])
    
    return {
        "answer": answer,
        "citations": results
    }


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
            "timestamp": datetime.now().isoformat()
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
        "timestamp": datetime.now().isoformat()
    }
    status_file.write_text(json.dumps(initial_status, indent=2))
    
    # Start background task
    asyncio.create_task(update_status_file())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
