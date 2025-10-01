"""RAG (Retrieval-Augmented Generation) module"""

from rag.llm_client import summarize_for_pdf
from rag.search import (
    delete_document,
    get_status,
    index_document,
    search,
    search_with_categories,
    search_with_synthesis,
)

__all__ = [
    "search",
    "index_document",
    "delete_document",
    "get_status",
    "search_with_synthesis",
    "search_with_categories",
    "summarize_for_pdf",
]
