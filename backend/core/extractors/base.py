"""
wizard404_core.extractors.base - Interfaz base para extractores.

Define el contrato Extractor y la función extract_metadata que delega
en el extractor adecuado según el tipo de archivo.
"""

from abc import ABC, abstractmethod
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


def extract_metadata(path: str | Path) -> Optional[DocumentMetadata]:
    """
    Extrae metadatos del archivo en path.
    Retorna None si el formato no está soportado.
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    extractor = _get_extractor_for(p)
    if not extractor:
        return None
    return extractor.extract(p)
