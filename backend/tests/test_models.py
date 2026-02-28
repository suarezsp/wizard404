"""
Tests de modelos del núcleo: DocumentMetadata, SearchFilters, SearchResult, DirectoryStats.
"""

from datetime import datetime

import pytest

from wizard404_core.models import (
    DocumentMetadata,
    SearchFilters,
    SearchResult,
    DirectoryStats,
)


def test_document_metadata_creation():
    meta = DocumentMetadata(
        path="/tmp/doc.pdf",
        name="doc.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
    )
    assert meta.path == "/tmp/doc.pdf"
    assert meta.name == "doc.pdf"
    assert meta.mime_type == "application/pdf"
    assert meta.size_bytes == 1024
    assert meta.content_preview == ""
    assert meta.content_full == ""


def test_document_metadata_extension():
    meta = DocumentMetadata(path="/a/b/file.TXT", name="file.TXT", mime_type="text/plain", size_bytes=0)
    assert meta.extension == ".txt"


def test_document_metadata_to_searchable_text():
    meta = DocumentMetadata(
        path="/x.pdf",
        name="Report 2024",
        mime_type="application/pdf",
        size_bytes=0,
        content_preview="Annual summary and budget",
    )
    text = meta.to_searchable_text()
    assert "report 2024" in text
    assert "annual summary" in text
    assert text == text.lower()


def test_search_filters_defaults():
    f = SearchFilters()
    assert f.query == ""
    assert f.mime_type is None
    assert f.min_size is None
    assert f.max_size is None
    assert f.limit == 50
    assert f.offset == 0
    assert f.order_by == "modified_at"
    assert f.order_desc is True
    assert f.date_field == "modified_at"
    assert f.name_pattern is None
    assert f.name_contains is None


def test_search_filters_with_all_optionals():
    dt = datetime(2024, 1, 15)
    f = SearchFilters(
        query="test",
        mime_type="text/plain",
        min_size=10,
        max_size=1000,
        from_date=dt,
        to_date=dt,
        directory="/data",
        limit=20,
        offset=5,
        order_by="name",
        order_desc=False,
        name_pattern="*.txt",
        name_contains="report",
        date_field="created_at",
    )
    assert f.query == "test"
    assert f.mime_type == "text/plain"
    assert f.min_size == 10
    assert f.max_size == 1000
    assert f.from_date == dt
    assert f.directory == "/data"
    assert f.limit == 20
    assert f.offset == 5
    assert f.order_by == "name"
    assert f.order_desc is False
    assert f.name_pattern == "*.txt"
    assert f.name_contains == "report"
    assert f.date_field == "created_at"


def test_search_result_defaults():
    r = SearchResult()
    assert r.id is None
    assert r.metadata is None
    assert r.snippet == ""
    assert r.score == 0.0


def test_search_result_with_metadata_and_snippet():
    meta = DocumentMetadata(path="/a.txt", name="a.txt", mime_type="text/plain", size_bytes=0)
    r = SearchResult(id=1, metadata=meta, snippet="...contrato...", score=15.0)
    assert r.id == 1
    assert r.metadata is not None
    assert r.metadata.name == "a.txt"
    assert r.snippet == "...contrato..."
    assert r.score == 15.0


def test_directory_stats_defaults():
    s = DirectoryStats()
    assert s.total_files == 0
    assert s.total_size == 0
    assert s.by_type == {}
    assert s.by_extension == {}


def test_directory_stats_with_data():
    s = DirectoryStats(
        total_files=5,
        total_size=1000,
        by_extension={".txt": 3, ".md": 2},
        by_type={"text/plain": 3, "text/markdown": 2},
    )
    assert s.total_files == 5
    assert s.total_size == 1000
    assert s.by_extension[".txt"] == 3
    assert s.by_type["text/plain"] == 3
