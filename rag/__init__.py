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
from rag.title_generator import extract_date_from_content, generate_title

__all__ = [
    "search",
    "index_document",
    "delete_document",
    "get_status",
    "search_with_synthesis",
    "search_with_categories",
    "summarize_for_pdf",
    "generate_title",
    "extract_date_from_content",
]
