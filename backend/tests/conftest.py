"""
Fixtures compartidas para pytest.
"""

import tempfile
from pathlib import Path

import pytest

"""Crea un archivo .txt de prueba."""
@pytest.fixture
def sample_txt_file(tmp_path: Path) -> Path:
    f = tmp_path / "sample.txt"
    f.write_text("Hello Wizard404. Este es un documento de prueba para búsqueda.")
    return f

"""Crea un archivo .md de prueba."""
@pytest.fixture
def sample_md_file(tmp_path: Path) -> Path: 
    f = tmp_path / "readme.md"
    f.write_text("# Título\n\nContenido de markdown con keywords: contrato, oferta.")
    return f
