"""
Validación de rutas del sistema de archivos para endpoints que operan sobre el servidor.

Compartido por import y scan para evitar duplicación (DRY). Solo rutas locales permitidas.
"""

from pathlib import Path

from fastapi import HTTPException

MAX_PATH_LEN = 4096


def validate_local_path(path: str, max_len: int = MAX_PATH_LEN) -> Path:
    """Valida path: longitud, ruta local (sin protocolo). Raises HTTPException si no es válido."""
    path = path.strip()
    if not path or len(path) > max_len:
        raise HTTPException(status_code=400, detail="Path invalid or too long")
    if path.startswith(("http://", "https://", "file://")):
        raise HTTPException(status_code=400, detail="Only local filesystem paths are allowed")
    p = Path(path)
    try:
        p = p.resolve()
    except (OSError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}")
    return p
