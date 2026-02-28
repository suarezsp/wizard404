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


def test_extract_docx_valid(sample_docx_file: Path):
    meta = extract_metadata(sample_docx_file)
    assert meta is not None
    assert meta.name == "sample.docx"
    assert "application/vnd.openxmlformats" in meta.mime_type
    assert "Wizard404" in meta.content_preview or "docx" in meta.content_preview.lower()
    assert meta.size_bytes > 0
    assert meta.extension == ".docx"


def test_extract_xlsx_valid(sample_xlsx_file: Path):
    meta = extract_metadata(sample_xlsx_file)
    assert meta is not None
    assert meta.name == "sample.xlsx"
    assert "spreadsheetml" in meta.mime_type
    assert "Wizard404" in meta.content_full or "xlsx" in meta.content_preview.lower() or meta.content_full
    assert meta.size_bytes > 0
    assert meta.extension == ".xlsx"


def test_extract_xlsx_corrupt_returns_metadata_with_empty_content(fake_xlsx_file: Path):
    """Archivo .xlsx que no es ZIP no debe lanzar; devuelve DocumentMetadata con is_corrupt=True."""
    meta = extract_metadata(fake_xlsx_file)
    assert meta is not None
    assert meta.name == "fake.xlsx"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.size_bytes > 0
    assert meta.is_corrupt is True


def test_extract_docx_corrupt_returns_metadata_with_empty_content(tmp_path: Path):
    """Archivo .docx que no es ZIP no debe lanzar; devuelve DocumentMetadata con is_corrupt=True."""
    f = tmp_path / "fake.docx"
    f.write_text("not a zip")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "fake.docx"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.is_corrupt is True


def test_extract_pdf_empty_returns_corrupt(tmp_path: Path):
    """PDF vacío no debe lanzar; devuelve DocumentMetadata con is_corrupt=True."""
    f = tmp_path / "empty.pdf"
    f.write_bytes(b"")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "empty.pdf"
    assert meta.is_corrupt is True
    assert meta.content_preview == ""
    assert meta.content_full == ""


def test_extract_pdf_invalid_content_returns_corrupt(tmp_path: Path):
    """Archivo con extensión .pdf pero contenido no-PDF no debe lanzar; is_corrupt=True."""
    f = tmp_path / "fake.pdf"
    f.write_text("not a pdf file")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "fake.pdf"
    assert meta.is_corrupt is True


def test_extract_image_corrupt_returns_corrupt(tmp_path: Path):
    """Imagen con extensión soportada pero contenido inválido devuelve is_corrupt=True."""
    f = tmp_path / "fake.png"
    f.write_bytes(b"not a valid png")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "fake.png"
    assert meta.is_corrupt is True


def test_extract_metadata_never_raises_for_supported_extension(tmp_path: Path):
    """extract_metadata no debe lanzar para archivos soportados (corruptos o no)."""
    files = [
        ("empty.pdf", b""),
        ("fake.docx", b"not zip"),
        ("fake.png", b"invalid"),
        ("bad.txt", b""),  # válido, solo vacío
    ]
    for name, content in files:
        p = tmp_path / name
        p.write_bytes(content)
        meta = extract_metadata(p)
        assert meta is not None, f"Expected metadata for {name}"


def test_extract_code_py(tmp_path: Path):
    """Archivo .py se extrae como texto y devuelve metadata."""
    f = tmp_path / "script.py"
    f.write_text("def hello():\n    print('Wizard404')")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "script.py"
    assert "text" in meta.mime_type.lower() or "python" in meta.mime_type.lower()
    assert "hello" in meta.content_preview or "Wizard404" in meta.content_preview
    assert meta.size_bytes > 0


def test_extract_code_c(tmp_path: Path):
    """Archivo .c se extrae como texto y devuelve metadata."""
    f = tmp_path / "main.c"
    f.write_text("int main() { return 0; }")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "main.c"
    assert "main" in meta.content_preview or "return" in meta.content_preview or len(meta.content_full or "") > 0
    assert meta.size_bytes > 0


def test_extract_binary_exe_metadata_only(tmp_path: Path):
    """Archivo .exe devuelve solo metadatos (sin contenido extraíble)."""
    f = tmp_path / "dummy.exe"
    f.write_bytes(b"MZ\x90\x00" + b"\x00" * 100)  # cabecera mínima
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "dummy.exe"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.size_bytes > 0
    assert meta.mime_type == "application/octet-stream"


def test_extract_media_mp4_metadata_only(tmp_path: Path):
    """Archivo .mp4 devuelve metadata minima (mime, size); content vacio."""
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00\x00\x00\x20ftypmp42")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "clip.mp4"
    assert meta.mime_type == "video/mp4"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.size_bytes > 0
    assert meta.is_corrupt is False


def test_extract_media_mp3_metadata_only(tmp_path: Path):
    """Archivo .mp3 devuelve metadata minima (mime, size); content vacio."""
    f = tmp_path / "song.mp3"
    f.write_bytes(b"ID3\x04\x00\x00\x00")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "song.mp3"
    assert meta.mime_type == "audio/mpeg"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.is_corrupt is False


def test_extract_media_heic_metadata_only(tmp_path: Path):
    """Archivo .heic devuelve metadata minima; content vacio."""
    f = tmp_path / "photo.heic"
    f.write_bytes(b"\x00\x00\x00\x18ftypheic")
    meta = extract_metadata(f)
    assert meta is not None
    assert meta.name == "photo.heic"
    assert meta.mime_type == "image/heic"
    assert meta.content_preview == ""
    assert meta.content_full == ""
    assert meta.is_corrupt is False
