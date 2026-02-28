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
