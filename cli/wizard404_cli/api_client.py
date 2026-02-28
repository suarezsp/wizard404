"""
Cliente HTTP para la API Wizard404.
Usa W404_API_URL (default http://127.0.0.1:8000) y W404_TOKEN o archivo de config
para listar y buscar documentos indexados. Backend debe estar en esa URL.
"""

import json
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

DEFAULT_API_URL = "http://127.0.0.1:8000"


def _config_token_path() -> Path:
    """Ruta al archivo de token; en Windows usa APPDATA si existe."""
    if platform.system() == "Windows" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "w404" / "token"
    return Path.home() / ".config" / "w404" / "token"


CONFIG_TOKEN_FILE = _config_token_path()
TOKEN_MSG = "Set W404_TOKEN (env) or save your token in ~/.config/w404/token. Have the backend running."


@dataclass
class IndexSearchResult:
    """Resultado de busqueda en el indice (API). Compatible con show_files_table y show_file_detail."""
    name: str
    path: str
    mime_type: str
    size_bytes: int
    content_preview: str = ""
    content_full: str = ""
    created_at: Any = None
    modified_at: Any = None
    id: int | None = None  # doc_id para GET /documents/{id}/summary


def get_api_config() -> tuple[str, str | None]:
    """
    Devuelve (base_url, token). base_url sale de W404_API_URL o default http://127.0.0.1:8000.
    Token desde env W404_TOKEN o, si no hay, desde archivo ~/.config/w404/token.
    token es None si no esta configurado en ningun sitio.
    """
    base = os.environ.get("W404_API_URL", "").strip()
    token = os.environ.get("W404_TOKEN", "").strip()
    if not token and CONFIG_TOKEN_FILE.exists():
        try:
            token = CONFIG_TOKEN_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return (base or DEFAULT_API_URL, token or None)


def _request_documents(
    path: str,
    params: dict[str, Any],
    token: str | None,
) -> tuple[list[dict], str | None]:
    """
    GET a la API. Devuelve (lista de dicts, error_message).
    Usa el token pasado si no es None; si no, lo lee de get_api_config().
    """
    base_url, config_tok = get_api_config()
    tok = token if token is not None else config_tok
    if not tok:
        return ([], TOKEN_MSG)
    url = base_url.rstrip("/") + path
    query_string = urlencode({k: v for k, v in params.items() if v is not None})
    full_url = f"{url}?{query_string}" if query_string else url
    req = Request(
        full_url,
        headers={"Authorization": f"Bearer {tok}"},
        method="GET",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 401:
            return ([], "Invalid or expired token.")
        if e.code == 404:
            return ([], "Backend not reachable or endpoint not found.")
        return ([], f"Backend error: {e.code}.")
    except (URLError, json.JSONDecodeError, OSError) as e:
        return ([], "Backend not reachable.")
    if not isinstance(data, list):
        return ([], "Invalid response from backend.")
    return (data, None)


def search_indexed(
    q: str,
    semantic: bool = False,
    mime_type: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[IndexSearchResult], str | None]:
    """
    GET /documents/search. Devuelve (resultados, error_message).
    semantic=True usa busqueda con expansion de consulta (mas recall).
    """
    _, token = get_api_config()
    if not token:
        return ([], TOKEN_MSG)
    params: dict[str, Any] = {"q": q, "limit": limit, "offset": offset}
    if semantic:
        params["semantic"] = "true"
    if mime_type:
        params["mime_type"] = mime_type
    if min_size is not None:
        params["min_size"] = min_size
    if max_size is not None:
        params["max_size"] = max_size
    data, err = _request_documents("/documents/search", params, token)
    if err:
        return ([], err)
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
                    id=item.get("id"),
                )
            )
    return (results, None)


def import_to_index(path: str) -> tuple[int, str | None]:
    """
    POST /documents/import con el path dado (archivo o directorio).
    Devuelve (numero de documentos importados, error_message). error_message None si ok.
    """
    base_url, token = get_api_config()
    if not token:
        return (0, TOKEN_MSG)
    url = base_url.rstrip("/") + "/documents/import"
    try:
        full_url = f"{url}?{urlencode({'path': path})}"
        req = Request(
            full_url,
            headers={"Authorization": f"Bearer {token}"},
            method="POST",
        )
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        try:
            body = e.read().decode()
            detail = json.loads(body).get("detail", str(e))
        except Exception:
            detail = str(e)
        return (0, f"API error: {detail}")
    except (URLError, json.JSONDecodeError, OSError):
        return (0, "Backend not reachable.")
    if not isinstance(data, dict):
        return (0, "Invalid response from backend.")
    imported = data.get("imported", 0)
    return (int(imported) if isinstance(imported, int) else 0, None)


def get_document_summary(doc_id: int) -> tuple[str | None, str | None]:
    """
    GET /documents/{doc_id}/summary. Devuelve (texto del resumen, error_message).
    """
    base_url, token = get_api_config()
    if not token:
        return (None, TOKEN_MSG)
    url = f"{base_url.rstrip('/')}/documents/{doc_id}/summary"
    try:
        req = Request(url, headers={"Authorization": f"Bearer {token}"}, method="GET")
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 404:
            return (None, "Document not found.")
        return (None, f"API error: {e.code}")
    except (URLError, json.JSONDecodeError, OSError):
        return (None, "Backend not reachable.")
    if isinstance(data, dict) and "summary" in data:
        return (data["summary"], None)
    return (None, "Invalid response.")


def list_indexed(
    limit: int = 200,
    offset: int = 0,
) -> tuple[list[IndexSearchResult], str | None]:
    """
    GET /documents: lista documentos indexados del usuario. Devuelve (resultados, error_message).
    """
    _, token = get_api_config()
    if not token:
        return ([], TOKEN_MSG)
    data, err = _request_documents("/documents", {"limit": limit, "offset": offset}, token)
    if err:
        return ([], err)
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
                    id=item.get("id"),
                )
            )
    return (results, None)
