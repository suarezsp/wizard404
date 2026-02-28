"""
wizard404_core.extractors.media - Metadata minima para video, audio e imagen HEIC/HEIF.

No extrae contenido; devuelve nombre, tamano, MIME y fechas para que estos archivos
aparezcan en scan, list by extension y organize por tipo.
"""

from datetime import datetime
from pathlib import Path

from wizard404_core.extractors.base import Extractor, register_extractor
from wizard404_core.models import DocumentMetadata

# MIME por extension (solo las que maneja este extractor)
_MEDIA_MIMES = {
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".mov": "video/quicktime",
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".m4v": "video/x-m4v",
    ".wmv": "video/x-ms-wmv",
    ".flv": "video/x-flv",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".wma": "audio/x-ms-wma",
}


class MediaExtractor(Extractor):
    """Extractor para video, audio y HEIC/HEIF: solo metadata, sin contenido."""

    supported_extensions = set(_MEDIA_MIMES.keys())

    def extract(self, path: Path) -> DocumentMetadata:
        """Devuelve metadatos basicos (path, name, size, mime, fechas); content vacio."""
        stat = path.stat()
        ext = path.suffix.lower()
        mime = _MEDIA_MIMES.get(ext, "application/octet-stream")
        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type=mime,
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview="",
            content_full="",
            is_corrupt=False,
        )


register_extractor(MediaExtractor())
