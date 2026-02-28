"""
Tests del backend launcher con mocks (sin levantar procesos reales).
"""

from unittest.mock import patch, MagicMock

import pytest

from wizard404_cli.backend_launcher import (
    _backend_responds,
    _start_backend,
    ensure_backend_running,
    _token_from_env_or_file,
    ensure_token,
    CONFIG_TOKEN_FILE,
)


def test_backend_responds_true_when_docs_ok():
    with patch("wizard404_cli.backend_launcher.urlopen") as m:
        m.return_value.__enter__ = MagicMock(return_value=MagicMock())
        m.return_value.__exit__ = MagicMock(return_value=False)
        assert _backend_responds("http://127.0.0.1:8000") is True


def test_backend_responds_false_when_fails():
    with patch("wizard404_cli.backend_launcher.urlopen") as m:
        m.side_effect = Exception("connection refused")
        assert _backend_responds("http://127.0.0.1:9999") is False


def test_ensure_backend_running_returns_true_when_already_up():
    with patch("wizard404_cli.backend_launcher._backend_responds", return_value=True):
        assert ensure_backend_running("http://127.0.0.1:8000") is True


def test_ensure_backend_running_starts_and_waits():
    with patch("wizard404_cli.backend_launcher._backend_responds") as m_responds:
        m_responds.side_effect = [False, False, True]  # third poll succeeds
        with patch("wizard404_cli.backend_launcher._start_backend", return_value=True):
            assert ensure_backend_running("http://127.0.0.1:8000") is True
        assert m_responds.call_count >= 3


def test_token_from_env():
    with patch.dict("os.environ", {"W404_TOKEN": "fake-token"}, clear=False):
        with patch("wizard404_cli.backend_launcher.CONFIG_TOKEN_FILE") as mock_path:
            mock_path.exists.return_value = False
            tok = _token_from_env_or_file()
            assert tok == "fake-token"


def test_ensure_token_true_when_already_has_token():
    with patch("wizard404_cli.backend_launcher._token_from_env_or_file", return_value="x"):
        assert ensure_token("http://127.0.0.1:8000") is True
