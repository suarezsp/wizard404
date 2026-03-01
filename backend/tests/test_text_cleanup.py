"""
Tests del módulo de limpieza de texto: clean_extracted_text y clean_metadata_text.
"""

import pytest
from wizard404_core.text_cleanup import clean_extracted_text, clean_metadata_text
from wizard404_core.models import DocumentMetadata
from datetime import datetime


def test_clean_extracted_text_empty_string():
    assert clean_extracted_text("") == ""


def test_clean_extracted_text_none_returns_empty():
    # Firma exige str; si se pasa None, no romper (retorna "")
    assert clean_extracted_text(None) == ""  # type: ignore[arg-type]


def test_clean_extracted_text_whitespace_only():
    assert clean_extracted_text("   \n\t  ") == ""


def test_clean_extracted_text_collapses_spaces_and_tabs():
    assert clean_extracted_text("word1   \t  word2\t\tword3") == "word1 word2 word3"


def test_clean_extracted_text_normalizes_line_endings():
    assert clean_extracted_text("a\r\nb\rc") == "a\nb\nc"


def test_clean_extracted_text_strips_per_line():
    assert clean_extracted_text("  hello  \n  world  ") == "hello\nworld"


def test_clean_metadata_text_returns_new_object():
    meta = DocumentMetadata(
        path="/x/file.txt",
        name="file.txt",
        mime_type="text/plain",
        size_bytes=10,
        content_preview="  foo  bar  ",
        content_full="  full  text  ",
    )
    result = clean_metadata_text(meta)
    assert result is not meta
    assert result.content_preview == "foo bar"
    assert result.content_full == "full text"
    assert result.path == meta.path
    assert result.name == meta.name
    assert result.mime_type == meta.mime_type
    assert result.size_bytes == meta.size_bytes


def test_clean_metadata_text_preserves_other_fields():
    created = datetime(2024, 1, 1)
    modified = datetime(2024, 2, 1)
    meta = DocumentMetadata(
        path="/a/b.pdf",
        name="b.pdf",
        mime_type="application/pdf",
        size_bytes=100,
        created_at=created,
        modified_at=modified,
        content_preview="dirty",
        content_full="dirty full",
        author="Author",
        title="Title",
        is_corrupt=False,
    )
    result = clean_metadata_text(meta)
    assert result.created_at is created
    assert result.modified_at is modified
    assert result.author == "Author"
    assert result.title == "Title"
    assert result.is_corrupt is False
    assert result.content_preview == "dirty"
    assert result.content_full == "dirty full"
