"""RAG (Retrieval-Augmented Generation) module"""

from rag.search import get_status, index_document, search

__all__ = ["search", "index_document", "get_status"]
