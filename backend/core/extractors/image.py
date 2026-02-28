"""
wizard404_core.extractors.image - Extracción de metadatos de imágenes.

Usa Pillow para dimensiones, modo, formato, DPI y EXIF completo.
content_preview: resumen corto (dimensiones + modo). content_full: todos los metadatos.
"""

from datetime import datetime
from pathlib import Path

from wizard404_core.extractors.base import Extractor, register_extractor
from wizard404_core.models import DocumentMetadata

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    _PILLOW_AVAILABLE = True
except ImportError:
    _PILLOW_AVAILABLE = False


def _exif_value_to_str(value) -> str:
    """Convierte un valor EXIF a string; maneja bytes y tipos no serializables."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace").strip()
        except Exception:
            return f"<bytes {len(value)}>"
    if hasattr(value, "decode"):  # Rational u otros
        try:
            return str(value)
        except Exception:
            return repr(value)
    return str(value)


class ImageExtractor(Extractor):
    """Extractor para archivos de imagen (dimensiones, EXIF completo, metadatos Pillow)."""

    supported_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif"}

    def extract(self, path: Path) -> DocumentMetadata:
        stat = path.stat()
        preview_parts = []
        full_parts = []

        if _PILLOW_AVAILABLE:
            try:
                with Image.open(path) as img:
                    w, h = img.size
                    preview_parts.append(f"{w}×{h} px")
                    if img.mode:
                        preview_parts.append(img.mode)

                    # Bloque "Imagen": dimensiones, modo, formato, DPI
                    full_parts.append("--- Imagen ---")
                    full_parts.append(f"Dimensiones: {w} × {h} px")
                    full_parts.append(f"Modo: {img.mode or 'N/A'}")
                    full_parts.append(f"Formato: {img.format or 'N/A'}")
                    if getattr(img, "info", None):
                        dpi = img.info.get("dpi")
                        if dpi is not None:
                            full_parts.append(f"DPI: {dpi}")

                    # EXIF completo
                    exif = img.getexif()
                    if exif:
                        full_parts.append("")
                        full_parts.append("--- EXIF ---")
                        for tag_id, value in exif.items():
                            if value is None or (isinstance(value, bytes) and len(value) == 0):
                                continue
                            tag = TAGS.get(tag_id, f"Tag_{tag_id}")
                            try:
                                val_str = _exif_value_to_str(value)
                                if val_str:
                                    full_parts.append(f"{tag}: {val_str}")
                            except Exception:
                                full_parts.append(f"{tag}: <no serializable>")
            except Exception as e:
                preview_parts.append(f"(error: {e})")
                full_parts.append(f"Error al leer imagen: {e}")
        else:
            preview_parts.append("(Pillow no instalado)")
            full_parts.append("Pillow no instalado; no se pueden extraer metadatos.")

        content_preview = " | ".join(preview_parts)
        content_full = "\n".join(full_parts) if full_parts else content_preview

        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type=self._mime_for(path.suffix),
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview=content_preview,
            content_full=content_full or content_preview,
        )

    def _mime_for(self, ext: str) -> str:
        mimes = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
        }
        return mimes.get(ext.lower(), "application/octet-stream")


if _PILLOW_AVAILABLE:
    register_extractor(ImageExtractor())
