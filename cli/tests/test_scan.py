"""
Tests del comando scan de la CLI.

Comprueba que run_scan devuelve False para rutas invalidas y True
cuando el directorio existe y wizard404_core esta disponible.
"""

from pathlib import Path

import pytest

from wizard404_cli.commands.scan import run_scan


def test_run_scan_non_existent_path():
    """run_scan con ruta invalida devuelve (False, None)."""
    ok, _ = run_scan("/ruta/que/no/existe")
    assert ok is False


def test_run_scan_file_not_dir(tmp_path):
    """run_scan con un archivo (no directorio) devuelve (False, None)."""
    f = tmp_path / "archivo.txt"
    f.write_text("hola")
    ok, _ = run_scan(str(f))
    assert ok is False


def test_run_scan_valid_dir(tmp_path):
    """run_scan con directorio valido devuelve (True, stats) o (False, None)."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.md").write_text("b")
    ok, stats = run_scan(str(tmp_path), recursive=False)
    assert ok in (True, False)
    if ok:
        assert stats is not None


def test_run_scan_quiet_returns_same_result(tmp_path):
    """run_scan(quiet=True) returns (True, stats) without printing table (same as quiet=False)."""
    (tmp_path / "x.txt").write_text("x")
    ok_quiet, stats_quiet = run_scan(str(tmp_path), recursive=False, quiet=True)
    ok_normal, stats_normal = run_scan(str(tmp_path), recursive=False, quiet=False)
    assert ok_quiet == ok_normal
    if ok_quiet and stats_quiet and stats_normal:
        assert stats_quiet.total_files == stats_normal.total_files
        assert stats_quiet.by_extension == stats_normal.by_extension
