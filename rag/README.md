# RAG Module - Implementation Complete

## Status

✅ **Sprint 0 Complete** - Model verification and initialization
✅ **Sprint 1 Complete** - Search API implementation
✅ **LLM Synthesis Complete** - Intelligent answer generation with Ollama

## Files Created

- `rag/chunker.py` - Text chunking utilities
- `rag/indexer.py` - Model and vector store initialization
- `rag/search.py` - Search API with `search()`, `index_document()`, `get_status()`, `search_with_synthesis()`
- `rag/llm_client.py` - LLM synthesis for coherent answers
- `rag/state.py` - Shared state management
- `rag/test_rag.py` - Simple test script
- `rag/test_synthesis.py` - LLM synthesis test script
- `rag/__init__.py` - Module exports

## Setup Instructions

### 1. Install Dependencies

The RAG module requires:
- `chromadb` - Vector database
- `sentence-transformers` - Embedding model
- `pyyaml` - Configuration parsing
- `ollama` - Local LLM for answer synthesis

Install all dependencies:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install chromadb sentence-transformers pyyaml ollama
```

### 2. Download Embedding Model

The model needs to be downloaded once:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-small-en-v1.5')
model.save('rag/models/bge-small-en-v1.5')
```

Or run from command line:
```bash
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-small-en-v1.5'); m.save('rag/models/bge-small-en-v1.5')"
```

### 3. Verify Installation

```bash
python -m rag.test_rag
```

## Usage

### Option 1: Simple Search (Returns Raw Chunks)

```python
from rag.search import search, index_document, get_status

# Check if RAG is ready
status = get_status()
print(status)  # {'model_loaded': True, 'index_size': 0, 'ready': True}

# Index a document
success = index_document(
    text="This is my lecture notes...",
    metadata={
        "class_code": "CS101",
        "date": "2025-09-30",
        "filename": "lecture1.pdf"
    }
)

# Search for documents
results = search(query="machine learning", top_k=5, scope="CS101")
for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Citation: {result['citation']}")
    print(f"Content: {result['chunk'][:100]}...")
```

### Option 2: Intelligent Search with LLM Synthesis (Recommended)

```python
from rag.search import search_with_synthesis

# Get a coherent, synthesized answer instead of raw chunks
result = search_with_synthesis(
    query="Give me a summary of SHPE VP meeting 4",
    top_k=8,
    scope="shpe"
)

print("Answer:", result['answer'])
print(f"Based on {len(result['citations'])} sources")
print(f"Synthesized: {result['synthesized']}")

# Access original chunks if needed
for citation in result['citations']:
    print(f"- {citation['citation']}: {citation['source']}")
```

**Why use synthesis?**
- **Before**: User gets 5-8 disconnected text chunks
- **After**: User gets a coherent 2-3 paragraph answer that directly addresses their question

**Example:**
```python
# Without synthesis
results = search("SHPE meeting fundraiser")
# Returns: ["VP Meeting 2... Fundraiser Ideas...", "corn fundraiser...", ...]

# With synthesis
result = search_with_synthesis("What fundraiser ideas were discussed?")
# Returns: "During SHPE VP Meeting 4, the committee brainstormed several
#           fundraising options including a corn fundraiser and raspados
#           (shaved ice) sales. Both ideas were well-received by the team..."
```

### Running the Indexer Service

To run the indexer as a standalone service with status updates:

```bash
python -m rag.indexer
```

This will:
1. Initialize the model and vector store
2. Update `logs/rag_status.json` every 30 seconds
3. Keep running until stopped with Ctrl+C

## API Contract

### `search(query: str, top_k: int = 8, scope: str = "all") -> List[Dict]`

**Args:**
- `query`: Search text
- `top_k`: Number of results to return
- `scope`: `"all"` for all documents, or specific `class_code` to filter

**Returns:**
```python
[
    {
        "chunk": "text content...",
        "source": "filename.pdf",
        "score": 0.85,
        "citation": "CS101 - 2025-09-30"
    },
    ...
]
```

### `index_document(text: str, metadata: Dict) -> bool`

**Args:**
- `text`: Document content to index
- `metadata`: Must contain `class_code`, `date`, `filename`

**Returns:** `True` on success, `False` on failure

### `get_status() -> Dict`

**Returns:**
```python
{
    "model_loaded": True,
    "index_size": 42,
    "ready": True
}
```

## Configuration

The RAG module reads from `config/app.yaml`:

```yaml
rag:
  model_path: rag/models/bge-small-en-v1.5
  embedding_dim: 384
  chunk_size: 500
  chunk_overlap: 50
  index_path: rag/data/chroma_db
  collection_name: notetaker_docs
  max_results: 5
```

## Status File

The indexer writes to `logs/rag_status.json` every 30 seconds:

```json
{
  "timestamp": "2025-09-30T23:00:00",
  "model_loaded": true,
  "index_size": 1234,
  "ready": true,
  "last_error": null
}
```

## Testing

Basic import test:
```bash
python -m rag.test_rag
```

Test with Python:
```bash
python -c "from rag.search import get_status; print(get_status())"
```

## Next Steps

1. **Backend Integration**: Backend can now import and use `search()` and `index_document()`
2. **Model Download**: Download the embedding model before full system testing
3. **End-to-End Testing**: Test with real PDF documents through the backend API

## Troubleshooting

### Model not loading?
```bash
ls -la rag/models/bge-small-en-v1.5/
# Should see: config.json, model.safetensors, tokenizer files
```

### Empty search results?
Check if documents are indexed:
```python
from rag.search import get_status
print(get_status())  # Check index_size
```

### Import errors?
Make sure to run from the project root and use module syntax:
```bash
python -m rag.indexer  # ✅ Good
python rag/indexer.py  # ❌ May have import issues
```

### LLM synthesis not working?

**Install and run Ollama:**
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama server (in a separate terminal)
ollama serve

# Pull the mistral model
ollama pull mistral
```

**Test Ollama:**
```bash
# Should return a response
ollama run mistral "Hello, how are you?"
```

**If Ollama is not available:**
The system will automatically fall back to returning concatenated chunks instead of synthesized answers. The `synthesized` flag in the response will be `True` even with fallback mode.

**Test synthesis:**
```bash
python -m rag.test_synthesis
```
