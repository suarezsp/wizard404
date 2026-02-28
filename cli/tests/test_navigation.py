"""
Tests de navegacion: run_list_detail_loop (volver a lista / volver al menu).
"""

from unittest.mock import patch

import pytest

from wizard404_cli.tui.common import run_list_detail_loop, display_type, display_name, display_type, display_name


def _fake_doc():
    """Objeto minimo con atributos que espera show_file_detail y show_files_table."""
    class Doc:
        path = "/tmp/fake.txt"
        name = "fake.txt"
        mime_type = "text/plain"
        size_bytes = 0
        content_preview = ""
        content_full = ""
        created_at = None
        modified_at = None
    return Doc()


def test_run_list_detail_loop_exits_on_enter():
    """Al responder Enter (vacío) a la primera pregunta, sale del bucle sin error."""
    items = [_fake_doc()]
    with patch("wizard404_cli.tui.common.Prompt") as mock_prompt:
        mock_prompt.ask.side_effect = [""]
        run_list_detail_loop(items, "Test title", count_label="file(s)")
    assert mock_prompt.ask.call_count == 1


def test_run_list_detail_loop_back_to_list_then_exit():
    """Ver detalle, Enter = volver a lista; luego Enter = salir."""
    items = [_fake_doc()]
    with patch("wizard404_cli.tui.common.Prompt") as mock_prompt:
        # Primera vez: elegir "1" para ver detalle
        # Segunda: "[Enter] Back to list" (cualquier cosa que no sea B)
        # Tercera: "" para salir
        mock_prompt.ask.side_effect = ["1", "", ""]
        run_list_detail_loop(items, "Test", count_label="item(s)")
    assert mock_prompt.ask.call_count >= 3


def test_display_type_without_subtype():
    """display_type returns mime_type when document_subtype is missing or None."""
    doc = _fake_doc()
    doc.mime_type = "application/pdf"
    assert display_type(doc) == "application/pdf"
    doc.document_subtype = None
    assert display_type(doc) == "application/pdf"


def test_display_type_with_scan_subtype():
    """display_type returns 'mime_type [scan]' when document_subtype is 'scan'."""
    doc = _fake_doc()
    doc.mime_type = "application/pdf"
    doc.document_subtype = "scan"
    assert display_type(doc) == "application/pdf [scan]"
