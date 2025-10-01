#!/usr/bin/env python3
"""
Sync vector DB index with files in inbox.
Re-indexes files that are missing from VDB.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import chromadb
import yaml

from rag.search import index_document

# Load config
config_path = project_root / "config/app.yaml"
with open(config_path) as f:
    cfg = yaml.safe_load(f)

inbox_path = project_root / cfg["paths"]["inbox_global"]


def get_indexed_files():
    """Get set of filenames currently in VDB"""
    try:
        client = chromadb.PersistentClient(str(project_root / "rag/index/chroma"))
        coll = client.get_collection("notes")
        docs = coll.get()
        filenames = set()
        for meta in docs["metadatas"]:
            if meta and "filename" in meta:
                filenames.add(meta["filename"])
        return filenames
    except Exception as e:
        print(f"❌ Failed to get indexed files: {e}")
        return set()


def sync_index():
    """Index any files missing from VDB"""
    print("🔄 Syncing vector DB with inbox files...")
    print()

    # Get currently indexed files
    indexed_files = get_indexed_files()
    print(f"📊 Current VDB status: {len(indexed_files)} files indexed")

    # Get all files in inbox
    txt_files = list(inbox_path.glob("*.txt"))
    print(f"📁 Files in inbox: {len(txt_files)}")
    print()

    # Find missing files
    missing = []
    for f in txt_files:
        if f.name not in indexed_files:
            missing.append(f)

    if not missing:
        print("✅ All files already indexed!")
        return 0

    print(f"⚠️  Found {len(missing)} files not in VDB:")
    for f in missing:
        print(f"   - {f.name}")
    print()

    # Index missing files
    indexed_count = 0
    for f in missing:
        print(f"📝 Indexing: {f.name}...")

        # Read file content
        try:
            text = f.read_text()
        except Exception as e:
            print(f"   ❌ Failed to read: {e}")
            continue

        # Load metadata from sidecar JSON if available
        meta_path = inbox_path / f"{f.stem}.meta.json"
        if meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text())
                # Ensure 'date' field exists for compatibility
                if "date" not in metadata:
                    metadata["date"] = (
                        metadata.get("content_date")
                        or metadata.get("upload_timestamp", "").split("T")[0]
                    )
            except Exception as e:
                print(f"   ⚠️  Failed to load metadata: {e}, using defaults")
                metadata = {
                    "filename": f.name,
                    "class_code": "GENERAL",
                    "date": "2025-10-01",
                }
        else:
            # Fallback: parse old filename format
            parts = f.stem.split("_", 1)
            if len(parts) > 1 and parts[0].count("-") == 2:
                metadata = {
                    "filename": f.name,
                    "class_code": parts[1],
                    "date": parts[0],
                }
            else:
                metadata = {
                    "filename": f.name,
                    "class_code": "GENERAL",
                    "date": "2025-10-01",
                }

        # Index the document
        success = index_document(text, metadata)
        if success:
            print(f"   ✅ Indexed successfully")
            indexed_count += 1
        else:
            print(f"   ❌ Indexing failed")

    print()
    print(f"✅ Sync complete: {indexed_count}/{len(missing)} files indexed")
    return 0


if __name__ == "__main__":
    sys.exit(sync_index())
