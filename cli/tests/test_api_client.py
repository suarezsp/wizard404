"""
Tests del cliente API (list_indexed, search_indexed) con mocks de urlopen.
Sin backend real; comprueba token ausente, 200 vacio, 200 con items, 401.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from wizard404_cli.api_client import (
    list_indexed,
    search_indexed,
    _request_documents,
    get_api_config,
    TOKEN_MSG,
    IndexSearchResult,
)


def test_list_indexed_returns_token_msg_when_no_token():
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", None)):
        results, err = list_indexed(limit=10, offset=0)
    assert results == []
    assert err == TOKEN_MSG


def test_search_indexed_returns_token_msg_when_no_token():
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", None)):
        results, err = search_indexed("foo", limit=10)
    assert results == []
    assert err == TOKEN_MSG


def test_list_indexed_returns_empty_list_on_200_empty():
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", "tk")):
        with patch("wizard404_cli.api_client.urlopen") as m_urlopen:
            resp = MagicMock()
            resp.read.return_value = json.dumps([]).encode()
            resp.__enter__ = MagicMock(return_value=resp)
            resp.__exit__ = MagicMock(return_value=False)
            m_urlopen.return_value = resp
            results, err = list_indexed(limit=10, offset=0)
    assert results == []
    assert err is None


def test_list_indexed_returns_index_search_results_on_200_with_items():
    payload = [
        {
            "id": 1,
            "name": "doc.pdf",
            "path": "/tmp/doc.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 1000,
            "snippet": "preview text",
        },
    ]
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", "tk")):
        with patch("wizard404_cli.api_client.urlopen") as m_urlopen:
            resp = MagicMock()
            resp.read.return_value = json.dumps(payload).encode()
            resp.__enter__ = MagicMock(return_value=resp)
            resp.__exit__ = MagicMock(return_value=False)
            m_urlopen.return_value = resp
            results, err = list_indexed(limit=10, offset=0)
    assert err is None
    assert len(results) == 1
    assert isinstance(results[0], IndexSearchResult)
    assert results[0].name == "doc.pdf"
    assert results[0].id == 1
    assert results[0].content_preview == "preview text"


def test_search_indexed_returns_empty_on_200_empty():
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", "tk")):
        with patch("wizard404_cli.api_client.urlopen") as m_urlopen:
            resp = MagicMock()
            resp.read.return_value = json.dumps([]).encode()
            resp.__enter__ = MagicMock(return_value=resp)
            resp.__exit__ = MagicMock(return_value=False)
            m_urlopen.return_value = resp
            results, err = search_indexed("query", limit=10)
    assert results == []
    assert err is None


def test_request_documents_uses_passed_token():
    """_request_documents usa el token pasado si no es None."""
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", "config-token")):
        with patch("wizard404_cli.api_client.urlopen") as m_urlopen:
            resp = MagicMock()
            resp.read.return_value = json.dumps([]).encode()
            resp.__enter__ = MagicMock(return_value=resp)
            resp.__exit__ = MagicMock(return_value=False)
            m_urlopen.return_value = resp
            data, err = _request_documents("/documents", {"limit": 10, "offset": 0}, "passed-token")
    assert err is None
    assert data == []
    # Request must use Bearer passed-token
    call_args = m_urlopen.call_args
    req = call_args[0][0]
    assert req.get_header("Authorization") == "Bearer passed-token"


def test_list_indexed_returns_error_on_401():
    with patch("wizard404_cli.api_client.get_api_config", return_value=("http://127.0.0.1:8000", "tk")):
        with patch("wizard404_cli.api_client.urlopen") as m_urlopen:
            from urllib.error import HTTPError
            m_urlopen.side_effect = HTTPError("http://x/documents", 401, "Unauthorized", {}, None)
            results, err = list_indexed(limit=10, offset=0)
    assert results == []
    assert "token" in (err or "").lower()
