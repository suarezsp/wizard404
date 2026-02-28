"""
wizard404_core.extractors.base - Interfaz base para extractores.

Define el contrato Extractor y la función extract_metadata que delega
en el extractor adecuado según el tipo de archivo. Si un extractor
lanza, se devuelve metadata minima con is_corrupt=True.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

from wizard404_core.models import DocumentMetadata


class Extractor(ABC):
    """Interfaz para extractores de documentos."""

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """Extensiones soportadas (ej: {'.pdf', '.txt'})."""
        pass

    @abstractmethod
    def extract(self, path: Path) -> DocumentMetadata:
        """Extrae metadatos y contenido del archivo."""
        pass


_EXTRACTORS: list[Extractor] = []


def register_extractor(extractor: Extractor) -> None:
    """Registra un extractor para ser usado por extract_metadata."""
    _EXTRACTORS.append(extractor)


def _get_extractor_for(path: Path) -> Optional[Extractor]:
    ext = path.suffix.lower()
    for ex in _EXTRACTORS:
        if ext in ex.supported_extensions:
            return ex
    return None


def _minimal_metadata_corrupt(p: Path) -> DocumentMetadata:
    """Metadata minima cuando el extractor falla; archivo sigue siendo listable/movible."""
    stat = p.stat()
    return DocumentMetadata(
        path=str(p.resolve()),
        name=p.name,
        mime_type="application/octet-stream",
        size_bytes=stat.st_size,
        created_at=datetime.fromtimestamp(stat.st_ctime),
        modified_at=datetime.fromtimestamp(stat.st_mtime),
        content_preview="",
        content_full="",
        is_corrupt=True,
    )


def extract_metadata(path: str | Path) -> Optional[DocumentMetadata]:
    """
    Extrae metadatos del archivo en path.
    Retorna None si el formato no está soportado.
    Si el extractor lanza, retorna metadata minima con is_corrupt=True.
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    extractor = _get_extractor_for(p)
    if not extractor:
        return None
    try:
        return extractor.extract(p)
    except Exception:
        return _minimal_metadata_corrupt(p)
