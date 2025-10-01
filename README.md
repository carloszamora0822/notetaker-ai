# 📚 NotesTaker AI - Intelligent Note Management System
An AI-powered note-taking platform that transforms raw lecture notes into searchable, beautifully formatted PDFs using RAG, local LLMs, and dynamic LaTeX generation.

## 🎯 Project Overview
NotesTaker AI is a full-stack web application that revolutionizes academic note-taking by combining modern AI technologies with professional document generation. The system automatically organizes, indexes, and formats notes while providing intelligent semantic search capabilities.

**Tech Stack:** Python • FastAPI • ChromaDB • Ollama • LangChain • LaTeX • Jinja2 • Sentence Transformers

## ✨ Key Features
### 🤖 AI-Powered Intelligence
- **Smart Title Generation:** Automatically generates descriptive titles from note content using local LLMs  
- **Date Extraction:** Intelligently parses and extracts dates from lecture notes  
- **Content Formatting:** LLM-based markdown formatting for improved readability  
- **Semantic Search:** RAG-powered search with context-aware answer synthesis  

### 📄 Professional PDF Generation
- **Dynamic LaTeX Compilation:** Converts notes to professionally formatted PDFs  
- **Class-Specific Themes:** Color-coded templates for different courses (AI, CS, Math, Physics, etc.)  
- **Custom Theme Editor:** Web-based UI for creating and managing visual themes  
- **Markdown Support:** Automatic conversion from markdown to LaTeX formatting  

### 🔍 Advanced Search & Retrieval
- **Vector Database:** ChromaDB-powered semantic search with sentence transformers  
- **Multi-Class Filtering:** Search across all notes or filter by specific courses  
- **Citation Tracking:** Results include source references and metadata  
- **LLM Synthesis:** Generates comprehensive answers from multiple note sources  

### 📁 Smart Organization
- **Automatic Class Registration:** Detects and registers new courses on upload  
- **Metadata Tracking:** Stores upload timestamps, content dates, and original filenames  
- **File Manager UI:** Web interface for browsing, viewing, and managing notes  
- **Duplicate Handling:** Smart filename generation to prevent overwrites  

## 🏗️ Architecture
### Backend (`backend/main.py`)
- FastAPI REST API with 25+ endpoints  
- Asynchronous request handling  
- Health monitoring for backend and Ollama services  
- Background task management for status tracking  

### RAG System (`rag/`)
- **Vector Indexing:** Sentence transformers + ChromaDB  
- **Document Chunking:** Smart text segmentation for optimal retrieval  
- **LLM Client:** Ollama integration for local inference  
- **Title Generator:** AI-powered metadata extraction  
- **Search Engine:** Multi-modal search with synthesis capabilities  

### LaTeX Generator (`latex/`)
- **Template System:** Dynamic theme injection  
- **Format Converter:** Markdown → LaTeX transformation  
- **Smart Formatting:** Auto-detection of lists, headers, and code blocks  
- **Escape Handling:** Safe LaTeX character escaping  

### Theme Manager (`config/`)
- **Dynamic Theming:** Per-class color palettes  
- **Persistent Storage:** Theme configuration management  
- **File Counting:** Automatic tracking of notes per class  

### Frontend (`frontend/templates/`)
- **Upload Interface:** Drag-and-drop file uploads with class selection  
- **Search Interface:** Real-time semantic search with cited results  
- **File Manager:** Browse, view, and delete notes with rich metadata  
- **Theme Editor:** Visual customization of class themes  

## 🚀 Technical Highlights
### 1. Intelligent Metadata System
```python
# Automatic metadata generation with AI title and date extraction
metadata = {
    "title": generate_title(text),           # AI-generated
    "content_date": extract_date(text),      # Parsed from content
    "upload_timestamp": datetime.now(),      # System timestamp
    "class_code": class_code.upper(),        # Normalized
    "original_filename": file.filename       # Preserved
}
```

### 2. RAG Pipeline
- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2  
- **Vector Store:** ChromaDB with persistent storage  
- **Retrieval:** Top-K similarity search with metadata filtering  
- **Synthesis:** LLM-generated answers with source citations  

### 3. Dynamic PDF Generation
```python
# LLM formats content → Markdown to LaTeX → Themed compilation
formatted_text = summarize_for_pdf(raw_text)
latex_content = generate_themed_latex(
    content=formatted_text,
    class_code="CS101",
    title=ai_generated_title,
    theme=get_theme("CS101")
)
compile_pdf(latex_content)
```

### 4. RESTful API Design
- `POST /ingest` - Upload notes with automatic processing  
- `POST /rag/query` - Semantic search with LLM synthesis  
- `GET /api/files` - List all notes with rich metadata  
- `GET /api/classes` - Retrieve class statistics  
- `GET /pdf/{filename}` - Serve compiled PDFs  
- `DELETE /api/file/{filename}` - Cascade delete (file + PDF + index)  

## 📊 Feature Breakdown
| Feature            | Technology                     | Implementation                                      |
|--------------------|--------------------------------|--------------------------------------------------|
| Backend API        | FastAPI + Uvicorn              | Async REST endpoints with Jinja2 templating      |
| Vector Search      | ChromaDB + Sentence Transformers | Persistent embeddings with semantic retrieval    |
| LLM Integration    | Ollama (local)                 | Title generation, formatting, answer synthesis   |
| Document Generation| LaTeX + pdflatex               | Dynamic themed PDFs with markdown support        |
| Database Sync      | Python scripts                 | Orphan cleanup and index synchronization         |
| Theme System       | YAML + Python                  | Per-class color schemes with visual editor       |
| File Management    | Pathlib + JSON                 | Metadata sidecars with duplicate handling        |

## 🛠️ Development Features
### Code Quality
- **Linting:** Black, Flake8, isort, Ruff  
- **Testing:** pytest + pytest-asyncio  
- **Pre-commit Hooks:** Automated formatting and validation  
- **Logging:** Comprehensive logging throughout the system  

### Makefile Automation
- Environment setup and dependency installation  
- Database synchronization scripts  
- Development server management  
- Code formatting and linting  

## 💡 Problem Solving
- **Challenge 1: Filename Conflicts**  
  Solution: Implemented intelligent duplicate detection with numeric suffixes (e.g., "Lecture Notes (2).txt")  

- **Challenge 2: LaTeX Special Characters**  
  Solution: Created robust escape function handling 10+ special characters with context awareness  

- **Challenge 3: Orphaned Vector Embeddings**  
  Solution: Built sync script to detect and remove database entries for deleted files  

- **Challenge 4: Content Date Ambiguity**  
  Solution: Prioritized content-extracted dates over upload timestamps for accurate chronology  

## 📈 Performance Considerations
- **Async Processing:** Non-blocking I/O for file uploads and LLM requests  
- **Caching:** Ollama model persistence for fast inference  
- **Batch Operations:** Efficient vector database operations  
- **Timeout Handling:** Graceful degradation when LLM services are unavailable  

## 🎓 Learning Outcomes
- Vector Databases: Hands-on experience with embeddings and semantic search  
- RAG Systems: End-to-end implementation of retrieval-augmented generation  
- Local LLMs: Integration with Ollama for privacy-focused AI  
- LaTeX Generation: Dynamic document creation with templating  
- FastAPI: Production-ready async web APIs  
- Full-Stack Development: Backend, database, and frontend integration  

## 🔧 Installation & Setup
```bash
# Clone and setup environment
git clone <repository-url>
cd notetaker-ai
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama (required for LLM features)
ollama serve

# Run the application
make start
# Or: uvicorn backend.main:app --reload

# Access
http://localhost:8000
```
