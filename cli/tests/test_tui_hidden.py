"""
Tests de la lógica TUI para archivos/directorios ocultos (nombre que empieza por '.').

Comprueban filter_hidden_paths y format_tree_entry sin depender del backend.
"""

from pathlib import Path

import pytest

from wizard404_cli.tui.common import filter_hidden_paths, format_tree_entry


def test_filter_hidden_paths_show_hidden_true_returns_all(tmp_path: Path):
    """Con show_hidden=True se devuelven todos los paths."""
    visible = tmp_path / "visible"
    visible.mkdir()
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    paths = sorted(tmp_path.iterdir(), key=lambda p: p.name)
    result = filter_hidden_paths(paths, show_hidden=True)
    assert len(result) == 2
    names = [p.name for p in result]
    assert ".hidden" in names
    assert "visible" in names


def test_filter_hidden_paths_show_hidden_false_filters_dot_prefix(tmp_path: Path):
    """Con show_hidden=False se excluyen los que empiezan por '.'."""
    (tmp_path / "a").mkdir()
    (tmp_path / ".b").mkdir()
    (tmp_path / "c").mkdir()
    paths = sorted(tmp_path.iterdir(), key=lambda p: p.name)
    result = filter_hidden_paths(paths, show_hidden=False)
    assert len(result) == 2
    names = [p.name for p in result]
    assert ".b" not in names
    assert "a" in names
    assert "c" in names


def test_format_tree_entry_visible_unchanged():
    """Entrada visible se devuelve sin modificar."""
    out = format_tree_entry("visible.txt", is_hidden=False)
    assert out == "visible.txt"


def test_format_tree_entry_hidden_has_suffix_no_ansi():
    """Entrada oculta lleva sufijo [hidden] y no contiene codigos ANSI (evita desalinear el menu)."""
    out = format_tree_entry(".hidden", is_hidden=True)
    assert ".hidden" in out
    assert "  [hidden]" in out
    assert "\033" not in out
