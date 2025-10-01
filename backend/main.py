"""
FastAPI backend for notetaker-ai
"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="notetaker-ai", version="0.1.0")

# Setup templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notetaker-ai"}


@app.get("/api/v1/info")
async def info():
    """API information"""
    return {
        "name": "notetaker-ai",
        "version": "0.1.0",
        "description": "AI-powered note taking with RAG and LaTeX support",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
