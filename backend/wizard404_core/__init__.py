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
    discover_and_extract_with_summary,
    list_files_by_extension,
    list_files_by_extension_with_metadata,
    list_subdirectories,
    list_files_in_directory,
    list_files_in_directory_with_metadata,
)
from wizard404_core.extractors import extract_metadata
from wizard404_core.search import search_documents, list_documents, apply_filters
from wizard404_core.semantic import expand_query, semantic_search_documents
from wizard404_core.embeddings import (
    encode as encode_embedding,
    cosine_similarity,
    embedding_from_json,
    get_model as get_embedding_model,
    search_by_embeddings,
)
from wizard404_core.summary import summarize_text
from wizard404_core.summary_scan import get_entropy_message
from wizard404_core.text_cleanup import clean_extracted_text, clean_metadata_text

__all__ = [
    "DocumentMetadata",
    "SearchFilters",
    "SearchResult",
    "discover_files",
    "analyze_directory",
    "discover_and_extract",
    "discover_and_extract_with_summary",
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
    "encode_embedding",
    "cosine_similarity",
    "embedding_from_json",
    "get_embedding_model",
    "search_by_embeddings",
    "summarize_text",
    "get_entropy_message",
    "clean_extracted_text",
    "clean_metadata_text",
]
