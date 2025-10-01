#!/usr/bin/env python3
"""
Clean up orphaned vectors in ChromaDB

Run: python ops/scripts/cleanup_orphans.py
"""

import sys
from pathlib import Path

import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def cleanup_orphaned_vectors():
    """Remove vectors for deleted files"""
    print("==> Checking for orphaned vectors in ChromaDB...")
    print()

    try:
        client = chromadb.PersistentClient(str(BASE_DIR / "rag/index/chroma"))
        coll = client.get_collection("notes")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        return 1

    inbox = BASE_DIR / "inbox"
    all_docs = coll.get()

    if not all_docs["ids"]:
        print("✓ No vectors in database")
        return 0

    deleted_count = 0
    checked_count = 0

    if all_docs["metadatas"]:
        # Group by filename to avoid duplicate checks
        file_to_ids = {}
        for idx, metadata in enumerate(all_docs["metadatas"]):
            filename = metadata.get("filename")
            if filename:
                if filename not in file_to_ids:
                    file_to_ids[filename] = []
                file_to_ids[filename].append(all_docs["ids"][idx])

        # Check each unique file
        for filename, doc_ids in file_to_ids.items():
            checked_count += 1
            if not (inbox / filename).exists():
                # Delete all vectors for this file
                coll.delete(ids=doc_ids)
                deleted_count += len(doc_ids)
                print(f"🗑️  Deleted {len(doc_ids)} vectors for: {filename}")

    print()
    print(f"✓ Checked {checked_count} unique files")
    print(f"✓ Total vectors in DB: {len(all_docs['ids'])}")

    if deleted_count > 0:
        print(f"✅ Cleanup complete: {deleted_count} orphaned vectors removed")
    else:
        print("✅ No orphaned vectors found")

    return 0


if __name__ == "__main__":
    sys.exit(cleanup_orphaned_vectors())
