"""
Tests de descubrimiento de archivos.
"""

from pathlib import Path

import pytest

from wizard404_core.discovery import discover_files, analyze_directory


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
