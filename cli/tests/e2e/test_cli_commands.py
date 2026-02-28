"""
Tests E2E de la CLI: ejecutan el comando real como subprocess.

Requieren ejecutarse desde la raíz del repo con PYTHONPATH=backend:cli,
o desde cli con PYTHONPATH que incluya backend.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND = REPO_ROOT / "backend"
CLI = REPO_ROOT / "cli"


def _run_cli(*args: str, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    py_path = os.environ.get("PYTHONPATH", "")
    new_path = f"{BACKEND}{os.pathsep}{CLI}"
    if py_path:
        new_path = f"{new_path}{os.pathsep}{py_path}"
    env = env or os.environ.copy()
    env["PYTHONPATH"] = new_path
    cmd = [sys.executable, "-m", "wizard404_cli.main", *args]
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_e2e_scan_directory(tmp_path: Path):
    """w404 scan <dir> con directorio válido termina con 0 y muestra estadísticas."""
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.md").write_text("# world")
    result = _run_cli("scan", str(tmp_path))
    assert result.returncode == 0
    assert "Scan" in result.stdout or "Total" in result.stdout or "files" in result.stdout.lower()


def test_e2e_scan_nonexistent():
    """w404 scan con ruta inexistente termina con código no cero."""
    result = _run_cli("scan", "/nonexistent/path/12345")
    assert result.returncode != 0


def test_e2e_search_help():
    """w404 search --help muestra ayuda."""
    result = _run_cli("search", "--help")
    assert result.returncode == 0
    assert "Keywords" in result.stdout or "search" in result.stdout.lower()
