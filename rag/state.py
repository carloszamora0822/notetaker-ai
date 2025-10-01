"""
Shared state for RAG system - single source of truth
"""
from typing import Optional
from sentence_transformers import SentenceTransformer

# Shared state - both indexer.py and search.py access these
model: Optional[SentenceTransformer] = None
collection = None
client = None
config: dict = {}
