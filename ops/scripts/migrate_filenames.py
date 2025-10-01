#!/usr/bin/env python3
"""
Migrate files from date-based naming to AI-generated titles

Usage:
    python ops/scripts/migrate_filenames.py [--dry-run] [--class CLASS_CODE]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import chromadb
import ollama
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_config():
    """Load application configuration"""
    config_file = BASE_DIR / "config/app.yaml"
    with open(config_file) as f:
        return yaml.safe_load(f)


def generate_title(content: str, model: str = "llama3.2:3b") -> str:
    """
    Generate AI title from content

    Args:
        content: File content to generate title from
        model: LLM model to use

    Returns:
        Generated title (max 60 chars)
    """
    # Take first 500 chars for title generation
    excerpt = content[:500].strip()

    prompt = f"""Generate a short, descriptive title (max 8 words) for these notes:

{excerpt}

Rules:
- Be specific and descriptive
- Include main topic
- No generic titles like "Notes" or "Meeting"
- Max 8 words
- No quotes or special characters
- Title case

Title:"""

    try:
        response = ollama.generate(
            model=model, prompt=prompt, options={"temperature": 0.3, "num_predict": 20}
        )

        title = response["response"].strip()
        # Clean up title
        title = title.strip("\"'")
        title = re.sub(r"[^\w\s-]", "", title)
        title = " ".join(title.split())

        # Truncate if too long
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    except Exception as e:
        print(f"⚠️  AI title generation failed: {e}")
        # Fallback: use first line
        first_line = excerpt.split("\n")[0][:60]
        return first_line if first_line else "Untitled Note"


def extract_date_and_class(filename: str) -> tuple:
    """
    Extract date and class code from filename

    Args:
        filename: e.g., "2025-10-01_AI.txt"

    Returns:
        (date_str, class_code) or (None, None)
    """
    match = re.match(r"(\d{4}-\d{2}-\d{2})_([A-Z0-9]+)\.txt$", filename)
    if match:
        return match.group(1), match.group(2)
    return None, None


def sanitize_filename(title: str) -> str:
    """Convert title to safe filename"""
    # Replace spaces with underscores
    safe = title.replace(" ", "_")
    # Remove special characters
    safe = re.sub(r"[^\w\-]", "", safe)
    # Collapse multiple underscores
    safe = re.sub(r"_+", "_", safe)
    # Trim length
    if len(safe) > 50:
        safe = safe[:50]
    return safe


def update_vector_db_metadata(old_filename: str, new_filename: str, date_str: str):
    """Update ChromaDB metadata for renamed file"""
    try:
        client = chromadb.PersistentClient(str(BASE_DIR / "rag/index/chroma"))
        coll = client.get_collection("notes")

        # Get all documents for this file
        all_docs = coll.get()

        if not all_docs["metadatas"]:
            return 0

        # Find matching documents
        matching_ids = []
        for idx, metadata in enumerate(all_docs["metadatas"]):
            if metadata.get("filename") == old_filename:
                matching_ids.append(all_docs["ids"][idx])

        if not matching_ids:
            return 0

        # Update metadata
        for doc_id in matching_ids:
            # Get current metadata
            result = coll.get(ids=[doc_id])
            if result["metadatas"]:
                metadata = result["metadatas"][0]
                # Update with new filename and date
                metadata["filename"] = new_filename
                metadata["upload_date"] = date_str

                # Re-add with updated metadata
                coll.update(ids=[doc_id], metadatas=[metadata])

        return len(matching_ids)

    except Exception as e:
        print(f"⚠️  Vector DB update failed: {e}")
        return 0


def migrate_file(file_path: Path, dry_run: bool = False) -> dict:
    """
    Migrate a single file

    Args:
        file_path: Path to file to migrate
        dry_run: If True, don't actually rename files

    Returns:
        Migration result dict
    """
    result = {
        "success": False,
        "old_name": file_path.name,
        "new_name": None,
        "title": None,
        "error": None,
        "vectors_updated": 0,
    }

    # Extract date and class
    date_str, class_code = extract_date_and_class(file_path.name)
    if not date_str or not class_code:
        result["error"] = "Invalid filename format"
        return result

    try:
        # Read content
        content = file_path.read_text(encoding="utf-8")

        # Generate title
        config = load_config()
        model = config.get("llm", {}).get("model", "llama3.2:3b")
        title = generate_title(content, model)
        result["title"] = title

        # Create new filename
        safe_title = sanitize_filename(title)
        new_filename = f"{date_str}_{class_code}_{safe_title}.txt"
        new_path = file_path.parent / new_filename

        # Check if target exists
        if new_path.exists():
            result["error"] = f"Target file already exists: {new_filename}"
            return result

        result["new_name"] = new_filename

        if not dry_run:
            # Rename text file
            file_path.rename(new_path)

            # Update vector DB
            vectors_updated = update_vector_db_metadata(
                file_path.name, new_filename, date_str
            )
            result["vectors_updated"] = vectors_updated

            # Rename associated PDF/TEX files if they exist
            base_name = file_path.stem  # e.g., "2025-10-01_AI"
            new_base = f"{date_str}_{class_code}_{safe_title}"

            # Check for PDF
            pdf_path = BASE_DIR / "latex/output" / f"{base_name}.pdf"
            if pdf_path.exists():
                pdf_path.rename(pdf_path.parent / f"{new_base}.pdf")

            # Check for TEX
            tex_path = BASE_DIR / "latex/output" / f"{base_name}.tex"
            if tex_path.exists():
                tex_path.rename(tex_path.parent / f"{new_base}.tex")

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def migrate_directory(directory: Path, class_filter: str = None, dry_run: bool = False):
    """
    Migrate all files in directory

    Args:
        directory: Directory to scan
        class_filter: Only migrate files for this class (optional)
        dry_run: If True, don't actually rename files
    """
    # Find all date-based files
    pattern = r"\d{4}-\d{2}-\d{2}_[A-Z0-9]+\.txt"
    files = [f for f in directory.glob("*.txt") if re.match(pattern, f.name)]

    if class_filter:
        files = [f for f in files if f"_{class_filter}." in f.name]

    if not files:
        print("✓ No files to migrate")
        return

    print(f"{'🔍 DRY RUN - ' if dry_run else ''}Found {len(files)} files to migrate\n")

    results = {"success": [], "failed": [], "skipped": []}

    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {file_path.name}")
        result = migrate_file(file_path, dry_run)

        if result["success"]:
            print(f"  ✓ {result['title']}")
            print(f"  → {result['new_name']}")
            if not dry_run and result["vectors_updated"]:
                print(f"  → Updated {result['vectors_updated']} vectors")
            results["success"].append(result)
        elif result["error"]:
            print(f"  ❌ {result['error']}")
            results["failed"].append(result)
        else:
            results["skipped"].append(result)

        print()

    # Summary
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"✓ Success: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⊘ Skipped: {len(results['skipped'])}")

    if dry_run:
        print("\n🔍 This was a dry run. No files were actually renamed.")
        print("   Run without --dry-run to apply changes.")


def main():
    parser = argparse.ArgumentParser(description="Migrate files to AI-generated titles")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--class", dest="class_code", help="Only migrate files for this class"
    )
    parser.add_argument(
        "--directory", default="inbox", help="Directory to migrate (default: inbox)"
    )

    args = parser.parse_args()

    directory = BASE_DIR / args.directory
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return 1

    print("=" * 60)
    print("File Migration to AI-Generated Titles")
    print("=" * 60)
    print(f"Directory: {directory}")
    if args.class_code:
        print(f"Class filter: {args.class_code}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    try:
        migrate_directory(directory, args.class_code, args.dry_run)
        return 0
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
