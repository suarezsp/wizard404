"""
Tests de busqueda y filtrado.
"""

from datetime import datetime

import pytest

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult
from wizard404_core.search import search_documents, list_documents


def _make_doc(name: str, path: str, content: str, size: int = 100) -> DocumentMetadata:
    return DocumentMetadata(
        path=path,
        name=name,
        mime_type="text/plain",
        size_bytes=size,
        modified_at=datetime(2024, 1, 15),
        content_preview=content,
        content_full=content,
    )


def test_search_by_keyword():
    docs = [
        _make_doc("a.txt", "/a.txt", "contrato de compra"),
        _make_doc("b.txt", "/b.txt", "informe de ventas"),
        _make_doc("c.txt", "/c.txt", "contrato de alquiler"),
    ]
    filters = SearchFilters(query="contrato", limit=10)
    results = search_documents(docs, filters)
    assert len(results) == 2
    assert all("contrato" in (r.metadata.content_preview if r.metadata else "") for r in results)


def test_search_filter_by_size():
    docs = [
        _make_doc("a.txt", "/a.txt", "a", size=50),
        _make_doc("b.txt", "/b.txt", "b", size=150),
        _make_doc("c.txt", "/c.txt", "c", size=200),
    ]
    filters = SearchFilters(min_size=100, max_size=180, limit=10)
    results = list_documents(docs, filters)
    assert len(results) == 1
    assert results[0].metadata and results[0].metadata.size_bytes == 150


def test_list_pagination():
    docs = [_make_doc(f"a{i}.txt", f"/a{i}.txt", "x") for i in range(10)]
    filters = SearchFilters(limit=3, offset=2)
    results = list_documents(docs, filters)
    assert len(results) == 3
