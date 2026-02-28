"""
Tests del modulo de carga (loading): run_with_loading_short, run_with_loading_long, run_with_loading_scan.

Comprueban que el resultado del worker se devuelve y que las excepciones se propagan.
"""

import pytest

from wizard404_cli.tui.loading import run_with_loading_short, run_with_loading_long, run_with_loading_scan


def test_run_with_loading_short_returns_worker_result():
    """run_with_loading_short devuelve el resultado del worker."""
    result = run_with_loading_short(lambda: 42)
    assert result == 42


def test_run_with_loading_short_with_args():
    """run_with_loading_short pasa argumentos al worker."""
    result = run_with_loading_short(lambda x, y: x + y, 10, 20)
    assert result == 30


def test_run_with_loading_short_worker_raises():
    """Si el worker lanza, la excepcion se propaga."""
    with pytest.raises(ValueError, match="oops"):
        run_with_loading_short(lambda: (_ for _ in ()).throw(ValueError("oops")))


def test_run_with_loading_long_returns_worker_result():
    """run_with_loading_long devuelve el resultado del worker (barra time-based)."""
    result = run_with_loading_long(lambda: "done")
    assert result == "done"


def test_run_with_loading_long_with_args():
    """run_with_loading_long pasa argumentos al worker."""
    result = run_with_loading_long(lambda a, b: a * b, 6, 7)
    assert result == 42


def test_run_with_loading_long_worker_raises():
    """Si el worker lanza, la excepcion se propaga."""
    with pytest.raises(RuntimeError, match="fail"):
        def failing():
            raise RuntimeError("fail")
        run_with_loading_long(failing)


def test_run_with_loading_scan_returns_worker_result():
    """run_with_loading_scan devuelve el resultado del worker (mensaje 'all done' 1s al final)."""
    result = run_with_loading_scan(lambda: 99)
    assert result == 99


def test_run_with_loading_scan_with_args():
    """run_with_loading_scan pasa argumentos al worker."""
    result = run_with_loading_scan(lambda a, b: a - b, 10, 3)
    assert result == 7
