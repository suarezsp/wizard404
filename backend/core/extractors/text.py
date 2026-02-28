"""
wizard404_core.extractors.text - Extracción de archivos de texto plano.

Soporta .txt, .md y similares. Lectura directa del contenido.
"""

from pathlib import Path
from datetime import datetime

from wizard404_core.extractors.base import Extractor, register_extractor
from wizard404_core.models import DocumentMetadata


class TextExtractor(Extractor):
    """Extractor para archivos de texto plano."""

    supported_extensions = {".txt", ".md", ".rst", ".log", ".csv"}

    def extract(self, path: Path) -> DocumentMetadata:
        stat = path.stat()
        content = path.read_text(encoding="utf-8", errors="replace")
        preview = content[:500].strip() if content else ""
        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type=self._mime_for(path.suffix),
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview=preview,
            content_full=content,
        )

    def _mime_for(self, ext: str) -> str:
        mimes = {".txt": "text/plain", ".md": "text/markdown", ".rst": "text/x-rst"}
        return mimes.get(ext.lower(), "text/plain")


register_extractor(TextExtractor())
