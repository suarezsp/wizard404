"""
wizard404_core - Núcleo reutilizable de Wizard404.

Librería que contiene la lógica de ingesta, extracción, indexado y búsqueda
de documentos. Consumida por la API FastAPI y por la CLI.
No depende de HTTP ni de frameworks web.
"""

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult
from wizard404_core.discovery import (
    discover_files,
    analyze_directory,
    discover_and_extract,
    list_files_by_extension,
    list_files_by_extension_with_metadata,
    list_subdirectories,
    list_files_in_directory,
    list_files_in_directory_with_metadata,
)
from wizard404_core.extractors import extract_metadata
from wizard404_core.search import search_documents, list_documents, apply_filters
from wizard404_core.semantic import expand_query, semantic_search_documents
from wizard404_core.summary import summarize_text
from wizard404_core.summary_scan import get_entropy_message

__all__ = [
    "DocumentMetadata",
    "SearchFilters",
    "SearchResult",
    "discover_files",
    "analyze_directory",
    "discover_and_extract",
    "list_files_by_extension",
    "list_files_by_extension_with_metadata",
    "list_subdirectories",
    "list_files_in_directory",
    "list_files_in_directory_with_metadata",
    "extract_metadata",
    "search_documents",
    "list_documents",
    "apply_filters",
    "expand_query",
    "semantic_search_documents",
    "summarize_text",
    "get_entropy_message",
]
