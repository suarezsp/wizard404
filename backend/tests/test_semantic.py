"""
Tests del módulo de búsqueda semántica (expansión de consulta).
"""

from datetime import datetime

import pytest

from wizard404_core.semantic import expand_query, semantic_search_documents
from wizard404_core.models import DocumentMetadata, SearchFilters


def test_expand_query_empty():
    assert expand_query("") == []
    assert expand_query("   ") == []


def test_expand_query_returns_lowercase():
    assert "contract" in expand_query("Contract")
    assert expand_query("Contract")[0] == "contract"


def test_expand_query_plural_stem():
    terms = expand_query("contracts")
    assert "contracts" in terms
    assert "contract" in terms


def test_expand_query_synonym_map():
    terms = expand_query("contract")
    assert "contract" in terms
    assert "contracts" in terms


def test_expand_query_informe():
    terms = expand_query("informe")
    assert "informe" in terms
    assert "informes" in terms


def test_semantic_search_documents_empty_query():
    docs = [
        DocumentMetadata(path="/a.txt", name="a.txt", mime_type="text/plain", size_bytes=10),
    ]
    filters = SearchFilters(query="", limit=10)
    results = semantic_search_documents(docs, filters)
    assert len(results) == 1
    assert results[0].metadata and results[0].metadata.name == "a.txt"


def test_semantic_search_documents_matches_expanded_term():
    """Buscar 'contract' debe encontrar documento con 'contracts'."""
    docs = [
        DocumentMetadata(
            path="/contracts.pdf",
            name="contracts.pdf",
            mime_type="application/pdf",
            size_bytes=100,
            content_preview="All contracts must be signed.",
        ),
    ]
    filters = SearchFilters(query="contract", limit=10)
    results = semantic_search_documents(docs, filters)
    assert len(results) == 1
    assert results[0].score > 0
    assert results[0].metadata and "contract" in results[0].metadata.content_preview.lower() or "contract" in results[0].metadata.name.lower()


def test_semantic_search_documents_pagination():
    docs = [
        DocumentMetadata(path=f"/f{i}.txt", name=f"f{i}.txt", mime_type="text/plain", size_bytes=1)
        for i in range(5)
    ]
    filters = SearchFilters(query="", limit=2, offset=1)
    results = semantic_search_documents(docs, filters)
    assert len(results) == 2
