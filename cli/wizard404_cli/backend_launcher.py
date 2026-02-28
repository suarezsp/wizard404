"""
Arranque del backend y obtencion de token por defecto.

Al ejecutar w404 (menu), se comprueba si el backend esta arriba; si no, se inicia
en segundo plano. Luego se asegura que exista token (registro o login w404/w404)
y se guarda en ~/.config/w404/token para que Index y Search en indice funcionen.
"""

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Ruta al backend (desde cli/wizard404_cli/)
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
DEFAULT_API_URL = "http://127.0.0.1:8000"


def _config_token_path() -> Path:
    """Ruta al archivo de token; en Windows usa APPDATA si existe para compatibilidad."""
    if platform.system() == "Windows" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "w404" / "token"
    return Path.home() / ".config" / "w404" / "token"


CONFIG_TOKEN_FILE = _config_token_path()
BACKEND_START_TIMEOUT = 20
BACKEND_POLL_INTERVAL = 0.5
DEFAULT_USER = "w404"
DEFAULT_PASSWORD = "w404"


def _backend_responds(base_url: str = DEFAULT_API_URL) -> bool:
    """Comprueba si el backend responde (GET /docs o raiz)."""
    try:
        req = Request(base_url.rstrip("/") + "/docs", method="GET")
        with urlopen(req, timeout=2) as _:
            return True
    except Exception:
        try:
            req = Request(base_url.rstrip("/") + "/", method="GET")
            with urlopen(req, timeout=2) as _:
                return True
        except Exception:
            return False
    return False


def _start_backend() -> bool:
    """Inicia uvicorn en segundo plano desde el directorio backend. Devuelve True si se lanzo."""
    if not _BACKEND_DIR.exists():
        return False
    if platform.system() == "Windows":
        venv_python = _BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = _BACKEND_DIR / "venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_BACKEND_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        subprocess.Popen(
            [python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(_BACKEND_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True
    except Exception:
        return False


def ensure_backend_running(base_url: str = DEFAULT_API_URL) -> bool:
    """
    Si el backend no responde, lo inicia y espera hasta que este listo.
    Devuelve True si el backend responde al final (ya estaba o se arranco).
    """
    if _backend_responds(base_url):
        return True
    _start_backend()
    deadline = time.monotonic() + BACKEND_START_TIMEOUT
    while time.monotonic() < deadline:
        if _backend_responds(base_url):
            return True
        time.sleep(BACKEND_POLL_INTERVAL)
    return False


def _token_from_env_or_file() -> str | None:
    """Token desde W404_TOKEN o desde archivo de config. None si no hay."""
    token = os.environ.get("W404_TOKEN", "").strip()
    if token:
        return token
    if CONFIG_TOKEN_FILE.exists():
        try:
            token = CONFIG_TOKEN_FILE.read_text(encoding="utf-8").strip()
            if token:
                return token
        except Exception:
            pass
    return None


def _register_or_login_and_save_token(base_url: str) -> bool:
    """
    Intenta registrar usuario w404/w404; si ya existe, hace login.
    Guarda el access_token en ~/.config/w404/token. Devuelve True si se guardo.
    """
    base = base_url.rstrip("/")
    register_url = base + "/auth/register"
    login_url = base + "/auth/login"
    data = json.dumps({"name": DEFAULT_USER, "password": DEFAULT_PASSWORD}).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    # Primero intentar registro; si el usuario ya existe (400), hacer login
    for url in (register_url, login_url):
        try:
            req = Request(url, data=data, headers=headers, method="POST")
            with urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())
                token = body.get("access_token") if isinstance(body, dict) else None
                if token:
                    try:
                        CONFIG_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                        CONFIG_TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
                    except OSError:
                        # Permisos o disco: no fallar; el token se usara en esta sesion via respuesta
                        pass
                    return True
        except HTTPError:
            # Register puede dar 400 si el usuario ya existe; en ese caso probamos login
            continue
        except (URLError, json.JSONDecodeError, OSError):
            return False
    return False


def ensure_token(base_url: str = DEFAULT_API_URL) -> bool:
    """
    Si no hay token (env o archivo), registra o hace login w404/w404 y guarda en archivo.
    Devuelve True si hay token al final.
    """
    if _token_from_env_or_file():
        return True
    if not _backend_responds(base_url):
        return False
    return _register_or_login_and_save_token(base_url)


def ensure_backend_and_token(base_url: str = DEFAULT_API_URL) -> None:
    """
    Orden: asegurar que el backend esta corriendo; luego asegurar token por defecto.
    Se llama antes de abrir el menu para que Index y Search en indice funcionen sin config.
    """
    ensure_backend_running(base_url)
    ensure_token(base_url)
