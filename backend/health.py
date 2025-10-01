"""Health check utilities for notetaker-ai services"""

from pathlib import Path

import chromadb


def check_vector_db_health(base_dir: Path) -> dict:
    """
    Check ChromaDB health and return stats

    Returns:
        {
            "status": "ok" | "error",
            "document_count": int,
            "collection_size": int,
            "orphaned_vectors": int
        }
    """
    try:
        client = chromadb.PersistentClient(str(base_dir / "rag/index/chroma"))
        coll = client.get_or_create_collection("notes")

        # Get all vectors
        all_docs = coll.get()
        total_vectors = len(all_docs["ids"])

        # Check for orphaned vectors (file doesn't exist)
        inbox = base_dir / "inbox"
        orphaned = 0
        unique_files = set()

        if all_docs["metadatas"]:
            unique_files = set(m.get("filename") for m in all_docs["metadatas"] if m.get("filename"))
            for filename in unique_files:
                if not (inbox / filename).exists():
                    orphaned += 1

        return {
            "status": "ok",
            "document_count": len(unique_files),
            "vector_count": total_vectors,
            "orphaned_files": orphaned,
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
