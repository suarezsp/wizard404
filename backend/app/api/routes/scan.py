"""
Endpoint Scan: analiza un directorio en el servidor y devuelve estadísticas.

Misma validación de path que import; solo directorios. Requiere autenticación.
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.api.path_utils import validate_local_path
from app.db.models import User
from wizard404_core.discovery import analyze_directory, list_files_by_extension_with_metadata

router = APIRouter(tags=["scan"])


class ScanResponse(BaseModel):
    """Estadísticas de un directorio escaneado (DirectoryStats)."""
    total_files: int
    total_size: int
    by_type: dict[str, int]
    by_extension: dict[str, int]


class ScanRequest(BaseModel):
    path: str


class ScanFileItem(BaseModel):
    """Un archivo listado en GET /scan/files."""
    name: str
    path: str
    size_bytes: int
    mime_type: str


def _scan_path(path: str) -> ScanResponse:
    p = validate_local_path(path)
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="Path must be a directory")
    try:
        stats = analyze_directory(p, recursive=True)
        return ScanResponse(
            total_files=stats.total_files,
            total_size=stats.total_size,
            by_type=stats.by_type,
            by_extension=stats.by_extension,
        )
    except OSError as e:
        raise HTTPException(status_code=503, detail=f"Scan failed: {e}") from e


@router.get("/scan", response_model=ScanResponse)
def get_scan(
    path: Annotated[str, Query(description="Directory path on server")] = "",
    current_user: User = Depends(get_current_user),
):
    """Escanea un directorio en el servidor y devuelve estadísticas por tipo y extensión."""
    if not path.strip():
        raise HTTPException(status_code=400, detail="path is required")
    return _scan_path(path)


@router.post("/scan", response_model=ScanResponse)
def post_scan(
    body: ScanRequest,
    current_user: User = Depends(get_current_user),
):
    """Escanea un directorio (path en body)."""
    if not body.path.strip():
        raise HTTPException(status_code=400, detail="path is required")
    return _scan_path(body.path.strip())


@router.get("/scan/files", response_model=list[ScanFileItem])
def get_scan_files(
    path: Annotated[str, Query(description="Directory path on server")] = "",
    extension: Annotated[str, Query(description="Filter by extension, e.g. .java")] = "",
    current_user: User = Depends(get_current_user),
):
    """Lista archivos de un directorio escaneado; opcionalmente filtrados por extension (con punto)."""
    if not path.strip():
        raise HTTPException(status_code=400, detail="path is required")
    p = validate_local_path(path)
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="Path must be a directory")
    ext = extension.strip().lower()
    if not ext.startswith("."):
        ext = f".{ext}" if ext else ""
    try:
        if ext:
            metas = list_files_by_extension_with_metadata(p, ext, recursive=True)
        else:
            from wizard404_core.discovery import discover_and_extract
            metas = list(discover_and_extract(p, recursive=True))
    except OSError as e:
        raise HTTPException(status_code=503, detail=f"Scan failed: {e}") from e
    return [
        ScanFileItem(name=m.name, path=m.path, size_bytes=m.size_bytes, mime_type=m.mime_type)
        for m in metas
    ]
