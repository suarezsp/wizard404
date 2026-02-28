"""
Tests de descubrimiento de archivos.
"""

from pathlib import Path

import pytest

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


def test_discover_files_in_directory(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.pdf").write_text("fake")  # pypdf puede fallar con contenido invalido
    (tmp_path / "c.xyz").write_text("c")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "d.md").write_text("d")
    found = list(discover_files(tmp_path))
    exts = {f.suffix.lower() for f in found}
    assert ".txt" in exts
    assert ".md" in exts
    assert ".xyz" not in exts


def test_discover_single_file(tmp_path: Path):
    f = tmp_path / "doc.txt"
    f.write_text("content")
    found = list(discover_files(f))
    assert len(found) == 1
    assert found[0].name == "doc.txt"


def test_analyze_directory(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a" * 10)
    (tmp_path / "b.txt").write_text("b" * 20)
    (tmp_path / "c.md").write_text("c")
    stats = analyze_directory(tmp_path)
    assert stats.total_files == 3
    assert stats.total_size >= 30
    assert stats.by_extension[".txt"] == 2
    assert stats.by_extension[".md"] == 1


def test_discover_and_extract_with_fake_xlsx_no_exception(discovery_tree: Path):
    """Con fake .xlsx (no ZIP) no debe lanzar; devuelve metas (fake con contenido vacío)."""
    metas = list(discover_and_extract(discovery_tree))
    exts = {m.extension for m in metas}
    assert ".txt" in exts
    assert ".md" in exts
    assert ".xlsx" in exts
    fake_meta = next((m for m in metas if m.name == "fake.xlsx"), None)
    assert fake_meta is not None
    assert fake_meta.content_preview == ""


def test_list_files_by_extension(discovery_tree: Path):
    txts = list_files_by_extension(discovery_tree, ".txt")
    assert len(txts) >= 2
    assert all(f.suffix.lower() == ".txt" for f in txts)
    empty = list_files_by_extension(discovery_tree, ".pdf")
    assert empty == []


def test_list_files_by_extension_with_metadata(discovery_tree: Path):
    metas = list_files_by_extension_with_metadata(discovery_tree, ".txt")
    assert len(metas) >= 2
    assert all(m.extension == ".txt" for m in metas)


def test_list_subdirectories(discovery_tree: Path):
    subdirs = list_subdirectories(discovery_tree)
    assert len(subdirs) == 1
    assert subdirs[0].name == "sub"
    assert list_subdirectories(discovery_tree / "sub") == []
    assert list_subdirectories(discovery_tree / "nonexistent") == []


def test_list_subdirectories_non_dir(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    assert list_subdirectories(f) == []


def test_list_subdirectories_includes_hidden_dirs(tmp_path: Path):
    """El core devuelve también directorios con nombre que empieza por '.'."""
    (tmp_path / "visible").mkdir()
    (tmp_path / ".hidden_dir").mkdir()
    subdirs = list_subdirectories(tmp_path)
    names = {d.name for d in subdirs}
    assert "visible" in names
    assert ".hidden_dir" in names


def test_list_files_in_directory(discovery_tree: Path):
    files = list_files_in_directory(discovery_tree)
    assert len(files) >= 3
    assert all(f.parent == discovery_tree for f in files)


def test_list_files_in_directory_with_metadata(discovery_tree: Path):
    metas = list_files_in_directory_with_metadata(discovery_tree)
    assert len(metas) >= 3
    assert all(m.name for m in metas)


def test_discover_files_nonexistent_path():
    found = list(discover_files("/nonexistent/path/xyz"))
    assert found == []


def test_discover_files_empty_dir(tmp_path: Path):
    found = list(discover_files(tmp_path))
    assert found == []


def test_discover_files_recursive_false(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("b")
    found = list(discover_files(tmp_path, recursive=False))
    assert len(found) == 1
    assert found[0].name == "a.txt"


def test_discover_media_extensions(tmp_path: Path):
    """Extensiones de media (.mp4, .mp3, .heic) se descubren y analizan con MIME correcto."""
    (tmp_path / "clip.mp4").write_bytes(b"\x00\x00\x00\x20ftypmp42")
    (tmp_path / "song.mp3").write_bytes(b"ID3\x04\x00\x00\x00")
    (tmp_path / "photo.heic").write_bytes(b"\x00\x00\x00\x18ftypheic")
    found = list(discover_files(tmp_path))
    exts = {f.suffix.lower() for f in found}
    assert ".mp4" in exts
    assert ".mp3" in exts
    assert ".heic" in exts
    stats = analyze_directory(tmp_path)
    assert stats.by_extension[".mp4"] == 1
    assert stats.by_extension[".mp3"] == 1
    assert stats.by_extension[".heic"] == 1
    assert "video/mp4" in stats.by_type
    assert "audio/mpeg" in stats.by_type
    assert "image/heic" in stats.by_type
