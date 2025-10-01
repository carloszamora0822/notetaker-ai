"""
Text chunking utilities for RAG system
"""
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks by tokens (approximate word-based).
    
    Args:
        text: Input text to chunk
        chunk_size: Approximate number of words per chunk (default: 500)
        overlap: Number of words to overlap between chunks (default: 50)
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    words = text.split()
    
    # If text is smaller than chunk size, return as single chunk
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
    
    return chunks
