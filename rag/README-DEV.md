# RAG Developer Guide

**Your Role**: Local embeddings, vector store, retrieval API for Backend.

---

## Your Workspace

```bash
cd /path/to/notetaker-ai/rag
source ../.venv/bin/activate
```

**Files you OWN**:
- `rag/indexer.py` - Main indexing logic
- `rag/search.py` - Search API (Sprint 1)
- `rag/index/` - Vector store persistence
- `rag/models/` - Local embedding model folder

**Files you READ** (do NOT edit):
- `config/app.yaml` - Model paths, chunk size

---

## Sprint 0 Tasks (2-4 hours)

### Task 1: Verify model folder
```python
# In indexer.py
from pathlib import Path
import yaml

CFG = yaml.safe_load(Path("../config/app.yaml").read_text())
MODEL_PATH = Path(CFG["embeddings"]["model_path"]).resolve()

if not MODEL_PATH.exists():
    print(f"\n[!] Missing model at: {MODEL_PATH}")
    print("Place 'bge-small-en-v1.5' folder in rag/models/\n")
    exit(1)
else:
    print(f"[OK] Model folder present: {MODEL_PATH}")
```

**Test**: `python rag/indexer.py` should print `[OK]`

### Task 2: Load embedding model
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(str(MODEL_PATH))
print(f"[OK] Model loaded: {model.get_sentence_embedding_dimension()} dims")
```

### Task 3: Initialize Chroma vector store
```python
import chromadb

client = chromadb.PersistentClient(path="rag/index/chroma")
collection = client.get_or_create_collection(name="notes")
print(f"[OK] Vector store ready: {collection.count()} documents")
```

### Task 4: Write status file
```python
import json
from datetime import datetime

def update_status():
    status = {
        "timestamp": datetime.now().isoformat(),
        "model_loaded": True,
        "index_size": collection.count(),
        "ready": True,
        "last_error": None
    }
    Path("logs/rag_status.json").write_text(json.dumps(status))

# Call every 30 seconds (use while loop or scheduler)
```

**Acceptance**:
- [ ] Model loads from `config["embeddings"]["model_path"]`
- [ ] Chroma DB initialized in `rag/index/chroma/`
- [ ] `logs/rag_status.json` updates every 30s
- [ ] Prints `[OK]` messages on startup

---

## Sprint 1 Tasks (4-8 hours)

### Task 1: Implement chunker
```python
# rag/chunker.py
def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    """Split text into overlapping chunks by tokens (approximate)"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
```

### Task 2: Implement `index_document()`
```python
# rag/search.py
def index_document(text: str, metadata: dict) -> bool:
    """
    Chunk text, embed, store in Chroma.
    metadata: {"class_code": str, "date": str, "filename": str}
    """
    try:
        chunks = chunk_text(text)
        embeddings = model.encode(chunks)

        ids = [f"{metadata['class_code']}_{metadata['date']}_chunk_{i}"
               for i in range(len(chunks))]

        collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[metadata] * len(chunks),
            ids=ids
        )
        return True
    except Exception as e:
        print(f"[ERROR] Indexing failed: {e}")
        return False
```

### Task 3: Implement `search()`
```python
# rag/search.py
def search(query: str, top_k: int = 8, scope: str = "all") -> List[dict]:
    """
    Semantic search in vector store.
    Returns: [{"chunk": str, "source": str, "score": float, "citation": str}, ...]
    """
    query_embedding = model.encode([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        where={"class_code": scope} if scope != "all" else None
    )

    output = []
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        output.append({
            "chunk": doc,
            "source": meta.get("filename", "unknown"),
            "score": 1.0 - dist,  # Convert distance to similarity
            "citation": f"{meta['class_code']} - {meta['date']}"
        })

    return output
```

### Task 4: Implement `get_status()`
```python
# rag/search.py
def get_status() -> dict:
    """Return current RAG status"""
    return {
        "model_loaded": model is not None,
        "index_size": collection.count(),
        "ready": model is not None and collection.count() >= 0
    }
```

**Acceptance**:
- [ ] `index_document()` adds text to vector store
- [ ] `search()` returns ranked results matching contract
- [ ] `get_status()` returns dict with keys: `model_loaded`, `index_size`, `ready`
- [ ] Backend can import: `from rag.search import search, index_document, get_status`

---

## Interface Contract (READ-ONLY)

See `docs/API-CONTRACTS.md`. You MUST provide:

```python
def search(query: str, top_k: int = 8, scope: str = "all") -> List[Dict]:
    """Returns: [{"chunk": str, "source": str, "score": float, "citation": str}]"""

def index_document(text: str, metadata: Dict) -> bool:
    """metadata: {"class_code": str, "date": str, "filename": str}"""

def get_status() -> Dict:
    """Returns: {"model_loaded": bool, "index_size": int, "ready": bool}"""
```

---

## Development Loop

```bash
# Run indexer
python rag/indexer.py

# Test search
python -c "from rag.search import search; print(search('test', top_k=3))"

# Check status file
cat logs/rag_status.json | jq '.'

# Format
black . && ruff . --fix

# Before commit
pre-commit run --all-files
git add -A && git commit -m "feat(rag): <what you did>"
```

---

## Debugging

### Model not loading?
```bash
ls -la rag/models/bge-small-en-v1.5/
# Should see: config.json, model.safetensors, tokenizer files
```

Download if missing:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
model.save('rag/models/bge-small-en-v1.5')
```

### Empty search results?
```python
# Check index size
collection.count()  # Should be > 0
collection.peek()   # View sample docs
```

### Backend can't import?
Verify `rag/search.py` exists and `rag/__init__.py` is present (even if empty).

---

## Rules (DO NOT VIOLATE)

1. ✅ Load model from `config["embeddings"]["model_path"]`
2. ✅ Store vectors in `rag/index/chroma/`
3. ✅ Update `logs/rag_status.json` every 30s
4. ✅ Return exact dict structure from `search()` (see contract)
5. ❌ Do NOT make HTTP calls - pure Python functions
6. ❌ Do NOT modify Backend, LaTeX, or Frontend code
7. ❌ Do NOT change interface without updating `docs/API-CONTRACTS.md`

---

## Need Help?

1. Check `docs/API-CONTRACTS.md` for interface spec
2. Verify model folder exists and is correct format
3. Check `logs/rag_status.json` for errors
4. Ask Manager (main IDE instance)
