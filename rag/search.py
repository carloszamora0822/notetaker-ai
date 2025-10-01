"""
RAG Search API - Interface for Backend to query vector store
"""
import logging
from typing import Dict, List

import rag.state as state
from rag.chunker import chunk_text
from rag.indexer import initialize_rag_system
from rag.llm_client import synthesize_answer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
            "n_results": min(
                top_k, state.collection.count()
            ),  # Don't request more than available
        }

        # Add scope filter if not "all"
        if scope != "all" and scope:
            # Normalize to uppercase for consistent matching
            normalized_scope = scope.upper()
            query_params["where"] = {"class_code": normalized_scope}
            logger.debug(f"Filtering by class: {normalized_scope}")

        # Execute query
        results = state.collection.query(**query_params)

        # Format results according to API contract
        output = []
        for i, (doc, meta, dist) in enumerate(
            zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ):
            output.append(
                {
                    "chunk": doc,
                    "source": meta.get("filename", "unknown"),
                    "score": 1.0 - dist,  # Convert distance to similarity score
                    "citation": f"{meta.get('class_code', 'unknown')} - {meta.get('date', 'unknown')}",
                }
            )

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

        # Normalize class_code to uppercase for consistent filtering
        metadata = metadata.copy()  # Don't modify original
        metadata["class_code"] = metadata["class_code"].upper()

        # Filter out None values - ChromaDB doesn't accept them
        metadata = {k: v for k, v in metadata.items() if v is not None}

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

        # Delete existing document if it exists (handle re-uploads)
        filename = metadata["filename"]
        try:
            existing = state.collection.get(where={"filename": filename})
            if existing["ids"]:
                logger.info(
                    f"🔄 Updating existing document: {filename} ({len(existing['ids'])} old chunks)"
                )
                state.collection.delete(ids=existing["ids"])
        except Exception as e:
            logger.debug(f"No existing document to delete: {e}")

        # Add to collection (upsert behavior)
        state.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[metadata] * len(chunks),
            ids=ids,
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


def delete_document(filename: str) -> bool:
    """
    Delete all chunks for a document from vector store

    Args:
        filename: Name of file to delete (e.g., "2025-10-01_AI.txt")

    Returns:
        True if deleted, False if failed
    """
    try:
        _ensure_initialized()

        if state.collection is None:
            logger.error("Collection not initialized")
            return False

        # Find all chunks for this file
        results = state.collection.get(where={"filename": filename})

        if not results["ids"]:
            logger.warning(f"No vectors found for {filename}")
            return False

        # Delete all chunks
        chunk_count = len(results["ids"])
        state.collection.delete(ids=results["ids"])
        logger.info(f"✅ Deleted {chunk_count} vectors for {filename}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to delete {filename}: {e}")
        return False


def search_with_synthesis(query: str, top_k: int = 8, scope: str = "all") -> Dict:
    """
    Search and synthesize results into a coherent answer

    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        scope: "all" or specific class_code to filter

    Returns:
        {
            "answer": str (synthesized by LLM),
            "citations": List[Dict] (original chunks),
            "synthesized": bool (True if LLM was used)
        }
    """
    # Get search results
    chunks = search(query, top_k=top_k, scope=scope)

    if not chunks:
        return {
            "answer": "I couldn't find any relevant notes for your query.",
            "citations": [],
            "synthesized": False,
        }

    # Synthesize with LLM
    answer = synthesize_answer(query, chunks)

    return {"answer": answer, "citations": chunks, "synthesized": True}


def search_with_categories(query: str, top_k: int = 8, scope: str = "all") -> Dict:
    """
    Search and group results by class and date

    Args:
        query: Search query
        top_k: Number of results to retrieve
        scope: "all" or specific class_code to filter

    Returns:
        {
            "results": [...],
            "by_class": {"AI": [...], "Database": [...]},
            "by_date": {"2025-10-01": [...], "2025-09-30": [...]},
            "total": int
        }
    """
    results = search(query, top_k, scope)

    # Group by class
    by_class = {}
    for r in results:
        # Extract class from citation (format: "CLASS_CODE - date")
        citation = r.get("citation", "")
        cls = citation.split(" - ")[0] if " - " in citation else "Unknown"

        if cls not in by_class:
            by_class[cls] = []
        by_class[cls].append(r)

    # Group by date
    by_date = {}
    for r in results:
        # Extract date from citation
        citation = r.get("citation", "")
        date = citation.split(" - ")[1] if " - " in citation else "Unknown"

        if date not in by_date:
            by_date[date] = []
        by_date[date].append(r)

    logger.info(
        f"Categorized {len(results)} results into {len(by_class)} classes and {len(by_date)} dates"
    )

    return {
        "results": results,
        "by_class": by_class,
        "by_date": by_date,
        "total": len(results),
    }


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
            "ready": state.model is not None and state.collection is not None,
        }

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {"model_loaded": False, "index_size": 0, "ready": False}
