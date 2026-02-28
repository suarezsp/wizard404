"""
Tests de busqueda y filtrado.
"""

from datetime import datetime

import pytest

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult
from wizard404_core.search import search_documents, list_documents, apply_filters


def _make_doc(
    name: str,
    path: str,
    content: str,
    size: int = 100,
    modified_at: datetime | None = None,
    created_at: datetime | None = None,
    mime_type: str = "text/plain",
) -> DocumentMetadata:
    dt = datetime(2024, 1, 15)
    return DocumentMetadata(
        path=path,
        name=name,
        mime_type=mime_type,
        size_bytes=size,
        modified_at=modified_at or dt,
        created_at=created_at or dt,
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


def test_apply_filters_mime_type():
    docs = [
        _make_doc("a.txt", "/a.txt", "x", mime_type="text/plain"),
        _make_doc("b.pdf", "/b.pdf", "y", mime_type="application/pdf"),
    ]
    out = apply_filters(docs, SearchFilters(mime_type="application/pdf"))
    assert len(out) == 1
    assert out[0].mime_type == "application/pdf"


def test_apply_filters_date_range():
    d1 = datetime(2024, 1, 1)
    d2 = datetime(2024, 6, 15)
    d3 = datetime(2024, 12, 31)
    docs = [
        _make_doc("a.txt", "/a.txt", "x", modified_at=d1),
        _make_doc("b.txt", "/b.txt", "y", modified_at=d2),
        _make_doc("c.txt", "/c.txt", "z", modified_at=d3),
    ]
    out = apply_filters(
        docs,
        SearchFilters(from_date=datetime(2024, 2, 1), to_date=datetime(2024, 7, 1)),
    )
    assert len(out) == 1
    assert out[0].name == "b.txt"


def test_apply_filters_directory():
    docs = [
        _make_doc("a.txt", "/data/docs/a.txt", "x"),
        _make_doc("b.txt", "/data/other/b.txt", "y"),
    ]
    out = apply_filters(docs, SearchFilters(directory="/data/docs"))
    assert len(out) == 1
    assert "docs" in out[0].path


def test_apply_filters_name_pattern():
    docs = [
        _make_doc("pepe-1.txt", "/p/pepe-1.txt", "x"),
        _make_doc("pepe-2.txt", "/p/pepe-2.txt", "y"),
        _make_doc("other.txt", "/p/other.txt", "z"),
    ]
    out = apply_filters(docs, SearchFilters(name_pattern="pepe-*.*"))
    assert len(out) == 2
    assert all("pepe-" in d.name for d in out)


def test_apply_filters_name_contains():
    docs = [
        _make_doc("report-2024.txt", "/r.txt", "x"),
        _make_doc("summary.txt", "/s.txt", "y"),
    ]
    out = apply_filters(docs, SearchFilters(name_contains="report"))
    assert len(out) == 1
    assert "report" in out[0].name


def test_apply_filters_empty_list():
    out = apply_filters([], SearchFilters(query="x"))
    assert out == []


def test_search_documents_empty_query_ordering():
    docs = [
        _make_doc("c.txt", "/c.txt", "x", modified_at=datetime(2024, 1, 1)),
        _make_doc("a.txt", "/a.txt", "y", modified_at=datetime(2024, 3, 1)),
    ]
    results = search_documents(docs, SearchFilters(query="", limit=10, order_by="modified_at", order_desc=True))
    assert len(results) == 2
    assert results[0].metadata and results[0].metadata.name == "a.txt"


def test_search_documents_limit_zero():
    docs = [_make_doc("a.txt", "/a.txt", "x")]
    results = search_documents(docs, SearchFilters(limit=0))
    assert len(results) == 0


def test_search_result_has_metadata_and_snippet():
    docs = [_make_doc("a.txt", "/a.txt", "contrato de compra")]
    results = search_documents(docs, SearchFilters(query="contrato", limit=10))
    assert len(results) == 1
    assert results[0].metadata is not None
    assert results[0].metadata.name == "a.txt"
    assert "contrato" in results[0].snippet


def test_search_order_by_name():
    docs = [
        _make_doc("z.txt", "/z.txt", "x"),
        _make_doc("a.txt", "/a.txt", "y"),
    ]
    results = search_documents(docs, SearchFilters(query="", order_by="name", order_desc=False, limit=10))
    assert results[0].metadata and results[0].metadata.name == "a.txt"


def test_search_order_by_size():
    docs = [
        _make_doc("big.txt", "/big.txt", "x", size=200),
        _make_doc("small.txt", "/small.txt", "y", size=50),
    ]
    results = search_documents(docs, SearchFilters(query="", order_by="size", order_desc=True, limit=10))
    assert results[0].metadata and results[0].metadata.size_bytes == 200


def test_search_multi_word_scores_both_terms_higher():
    """Multi-word query: doc with both terms scores higher than doc with one."""
    docs = [
        _make_doc("solo_informe.txt", "/a.txt", "Este es un informe detallado."),
        _make_doc("informe_anual.txt", "/b.txt", "Informe anual de la empresa 2024."),
    ]
    filters = SearchFilters(query="informe anual", limit=10)
    results = search_documents(docs, filters)
    assert len(results) == 2
    # First result should be the one with both terms (higher score)
    assert results[0].metadata and results[0].metadata.name == "informe_anual.txt"
    assert results[0].score >= results[1].score


def test_search_multi_word_snippet_has_context():
    """Snippet includes context around first matching token."""
    content = "A" * 100 + "contrato" + "B" * 100
    docs = [_make_doc("doc.txt", "/doc.txt", content)]
    results = search_documents(docs, SearchFilters(query="contrato venta", limit=10))
    assert len(results) == 1
    assert "contrato" in results[0].snippet
    assert len(results[0].snippet) > 20


def test_search_multi_word_filters_any_token():
    """Documents matching any query token are included."""
    docs = [
        _make_doc("a.txt", "/a.txt", "solo palabra uno"),
        _make_doc("b.txt", "/b.txt", "solo palabra dos"),
    ]
    results = search_documents(docs, SearchFilters(query="uno dos", limit=10))
    assert len(results) == 2
