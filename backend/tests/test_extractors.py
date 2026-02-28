"""
Tests de extractores de documentos.
"""

from pathlib import Path

import pytest

from wizard404_core.extractors import extract_metadata
from wizard404_core.models import DocumentMetadata


def test_extract_txt(sample_txt_file: Path):
    meta = extract_metadata(sample_txt_file)
    assert meta is not None
    assert meta.name == "sample.txt"
    assert meta.mime_type == "text/plain"
    assert "Wizard404" in meta.content_preview
    assert meta.size_bytes > 0


def test_extract_md(sample_md_file: Path):
    meta = extract_metadata(sample_md_file)
    assert meta is not None
    assert meta.name == "readme.md"
    assert "contrato" in meta.content_preview
    assert meta.extension == ".md"


def test_extract_unsupported_returns_none(tmp_path: Path):
    f = tmp_path / "file.xyz"
    f.write_text("xyz")
    assert extract_metadata(f) is None


def test_extract_nonexistent_returns_none():
    assert extract_metadata("/nonexistent/path/file.txt") is None
