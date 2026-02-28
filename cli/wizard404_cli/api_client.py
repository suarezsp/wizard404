"""
wizard404_cli.api_client - Cliente HTTP para la API de Wizard404.

Usa W14_API_URL y W14_TOKEN para buscar en documentos indexados.
"""

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


@dataclass
class IndexSearchResult:
    """Resultado de búsqueda en el índice (API). Compatible con _show_files_table y _show_file_detail."""
    name: str
    path: str
    mime_type: str
    size_bytes: int
    content_preview: str = ""
    content_full: str = ""
    created_at: Any = None
    modified_at: Any = None


def get_api_config() -> tuple[str | None, str | None]:
    """Devuelve (base_url, token) desde W14_API_URL y W14_TOKEN. None si no configurado."""
    base = os.environ.get("W14_API_URL", "").strip()
    token = os.environ.get("W14_TOKEN", "").strip()
    return (base or None, token or None)


def search_indexed(
    q: str,
    mime_type: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[IndexSearchResult]:
    """
    GET /documents/search en la API. Requiere W14_API_URL y W14_TOKEN.
    Devuelve lista de IndexSearchResult o lista vacía si falla/no configurado.
    """
    base_url, token = get_api_config()
    if not base_url or not token:
        return []
    url = base_url.rstrip("/") + "/documents/search"
    params: dict[str, Any] = {"q": q, "limit": limit, "offset": offset}
    if mime_type:
        params["mime_type"] = mime_type
    if min_size is not None:
        params["min_size"] = min_size
    if max_size is not None:
        params["max_size"] = max_size
    query_string = urlencode({k: v for k, v in params.items() if v is not None})
    full_url = f"{url}?{query_string}"
    req = Request(
        full_url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (HTTPError, URLError, json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    results: list[IndexSearchResult] = []
    for item in data:
        if isinstance(item, dict):
            results.append(
                IndexSearchResult(
                    name=item.get("name", ""),
                    path=item.get("path", ""),
                    mime_type=item.get("mime_type", ""),
                    size_bytes=int(item.get("size_bytes", 0)),
                    content_preview=item.get("snippet", ""),
                    content_full=item.get("snippet", ""),
                )
            )
    return results
