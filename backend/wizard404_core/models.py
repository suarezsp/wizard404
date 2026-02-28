"""
DTOs y estructuras de datos del nucleo.

Define DocumentMetadata, SearchFilters y SearchResult usados por
extractors, indexer y search. Mantiene el core libre de dependencias
de base de datos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

"""Metadatos extraidos de un documento."""
@dataclass
class DocumentMetadata:
    path: str
    name: str
    mime_type: str
    size_bytes: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    content_preview: str = ""
    content_full: str = ""
    is_corrupt: bool = False  # True si no se pudo extraer contenido (archivo movible/listable)
    document_subtype: Optional[str] = None  # e.g. "scan" for image-only PDFs, "encrypted", "corrupt"

    @property
    def extension(self) -> str:
        return Path(self.path).suffix.lower()

    def to_searchable_text(self) -> str:
        """Texto normalizado para busqueda (title + preview)."""
        return f"{self.name} {self.content_preview}".lower()

"""Filtros para busqueda y listado de documentos."""
@dataclass
class SearchFilters:
    query: str = ""
    mime_type: Optional[str] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    directory: Optional[str] = None
    limit: int = 50
    offset: int = 0
    order_by: str = "modified_at"
    order_desc: bool = True
    name_pattern: Optional[str] = None  # fnmatch (ej. pepe-*.*)
    date_field: str = "modified_at"  # "modified_at" | "created_at"
    name_contains: Optional[str] = None  # texto que debe contener el nombre

"""Resultado de busqueda con metadatos y snippet."""
@dataclass
class SearchResult:
    id: Optional[int] = None
    metadata: Optional[DocumentMetadata] = None
    snippet: str = ""
    score: float = 0.0


"""Estadisticas agregadas de un directorio escaneado."""
@dataclass
class DirectoryStats:
    total_files: int = 0
    total_size: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_extension: dict[str, int] = field(default_factory=dict)
