"""
RAG Search API - Interface for Backend to query vector store
"""
import logging
from typing import Dict, List

import rag.state as state
from rag.chunker import chunk_text
from rag.indexer import initialize_rag_system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the system on module import
_initialized = False


def _ensure_initialized():
    """Ensure RAG system is initialized before use"""
    global _initialized
    if not _initialized:
        logger.info("Initializing RAG system...")
        if initialize_rag_system():
            _initialized = True
            logger.info("RAG system initialized successfully")
        else:
            logger.error("RAG system initialization failed")
            raise RuntimeError("RAG system is not initialized")


def search(query: str, top_k: int = 8, scope: str = "all") -> List[Dict]:
    """
    Semantic search in vector store.
    
    Args:
        query: search text
        top_k: number of results to return
        scope: "all" to search all documents, or class_code to filter by class
        
    Returns:
        List of dicts with keys: chunk, source, score, citation
        [{"chunk": str, "source": str, "score": float, "citation": str}, ...]
    """
    try:
        _ensure_initialized()
        
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        if state.model is None:
            logger.error("Model not loaded")
            return []
        
        if state.collection is None:
            logger.error("Collection not initialized")
            return []
        
        # Check if collection has any documents
        if state.collection.count() == 0:
            logger.warning("Vector store is empty, no documents indexed")
            return []
        
        # Encode the query
        query_embedding = state.model.encode([query])[0]
        
        # Build query parameters
        query_params = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": min(top_k, state.collection.count())  # Don't request more than available
        }
        
        # Add scope filter if not "all"
        if scope != "all" and scope:
            query_params["where"] = {"class_code": scope}
        
        # Execute query
        results = state.collection.query(**query_params)
        
        # Format results according to API contract
        output = []
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            output.append({
                "chunk": doc,
                "source": meta.get("filename", "unknown"),
                "score": 1.0 - dist,  # Convert distance to similarity score
                "citation": f"{meta.get('class_code', 'unknown')} - {meta.get('date', 'unknown')}"
            })
        
        logger.info(f"Search completed: query='{query[:50]}...', results={len(output)}")
        return output
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


def index_document(text: str, metadata: Dict) -> bool:
    """
    Chunk text, embed, and store in Chroma vector store.
    
    Args:
        text: document content to index
        metadata: dict with keys: class_code, date, filename
                 {"class_code": str, "date": str, "filename": str}
    
    Returns:
        True on success, False on failure
    """
    try:
        _ensure_initialized()
        
        if not text or not text.strip():
            logger.warning("Empty text provided for indexing")
            return False
        
        if state.model is None:
            logger.error("Model not loaded, cannot index document")
            return False
        
        if state.collection is None:
            logger.error("Collection not initialized")
            return False
        
        # Validate metadata
        required_keys = ["class_code", "date", "filename"]
        for key in required_keys:
            if key not in metadata:
                logger.error(f"Missing required metadata key: {key}")
                return False
        
        # Chunk the text
        chunks = chunk_text(text)
        
        if not chunks:
            logger.warning("No chunks generated from text")
            return False
        
        logger.info(f"Chunking complete: {len(chunks)} chunks")
        
        # Encode chunks
        embeddings = state.model.encode(chunks)
        
        # Generate unique IDs for each chunk
        base_id = f"{metadata['class_code']}_{metadata['date']}_{metadata['filename']}"
        ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Add to collection
        state.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[metadata] * len(chunks),
            ids=ids
        )
        
        logger.info(
            f"Document indexed successfully: "
            f"file={metadata['filename']}, chunks={len(chunks)}, "
            f"class={metadata['class_code']}"
        )
        return True
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return False


def get_status() -> Dict:
    """
    Return current RAG status.
    
    Returns:
        Dict with keys: model_loaded, index_size, ready
        {"model_loaded": bool, "index_size": int, "ready": bool}
    """
    try:
        # Try to ensure initialization, but don't fail if it doesn't work
        try:
            _ensure_initialized()
        except Exception:
            pass
        
        return {
            "model_loaded": state.model is not None,
            "index_size": state.collection.count() if state.collection else 0,
            "ready": state.model is not None and state.collection is not None
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {
            "model_loaded": False,
            "index_size": 0,
            "ready": False
        }
