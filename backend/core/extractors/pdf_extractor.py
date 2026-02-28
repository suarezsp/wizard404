"""
wizard404_core.extractors.pdf_extractor - Extracción de PDFs.

Usa pypdf para extraer texto y metadatos básicos.
"""

from pathlib import Path
from datetime import datetime

from wizard404_core.extractors.base import Extractor, register_extractor
from wizard404_core.models import DocumentMetadata


class PDFExtractor(Extractor):
    """Extractor para archivos PDF."""

    supported_extensions = {".pdf"}

    def extract(self, path: Path) -> DocumentMetadata:
        from pypdf import PdfReader

        stat = path.stat()
        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages[:10]:  # Primeras 10 páginas para preview
            t = page.extract_text()
            if t:
                text_parts.append(t)
        content = "\n".join(text_parts)
        preview = content[:500].strip() if content else ""

        # Metadatos del documento PDF (autor, título, creador, etc.)
        content_full = content
        if reader.metadata:
            meta_lines = ["--- Metadatos PDF ---"]
            for attr, label in (
                ("author", "Author"),
                ("title", "Title"),
                ("subject", "Subject"),
                ("creator", "Creator"),
                ("producer", "Producer"),
            ):
                val = getattr(reader.metadata, attr, None)
                if val is not None and str(val).strip():
                    meta_lines.append(f"{label}: {val}")
            if len(meta_lines) > 1:
                content_full = "\n".join(meta_lines) + "\n\n--- Texto ---\n" + (content or "(sin texto extraíble)")

        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type="application/pdf",
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview=preview,
            content_full=content_full,
        )


register_extractor(PDFExtractor())
