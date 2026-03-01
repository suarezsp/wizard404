"""
Limpieza de texto extraído antes de persistir e indexar.

El material de diseño recomienda normalizar el texto antes de indexar:
"Un indexador no funciona bien con texto sucio. Dedicad 10 minutos a limpiar."
Se aplica una sola vez en el flujo de importación (servicio), no en cada extractor.
Solo stdlib; sin dependencias externas.
"""

from wizard404_core.models import DocumentMetadata


def clean_extracted_text(text: str) -> str:
    """
    Normaliza texto extraído: saltos de línea y espacios.
    Entrada: texto en bruto; salida: texto normalizado (sin cambiar semántica).
    """
    if not text or not isinstance(text, str):
        return ""
    # Normalizar saltos de línea
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalizar espacios: colapsar secuencias de espacios/tabs en un solo espacio
    lines = t.split("\n")
    cleaned_lines = []
    for line in lines:
        words = line.split()
        cleaned_lines.append(" ".join(words) if words else "")
    return "\n".join(cleaned_lines).strip()


def clean_metadata_text(meta: DocumentMetadata) -> DocumentMetadata:
    """
    Devuelve un nuevo DocumentMetadata con content_preview y content_full
    normalizados mediante clean_extracted_text. El resto de campos se copian.
    No muta el original.
    """
    clean_preview = clean_extracted_text(meta.content_preview or "")
    clean_full = clean_extracted_text(meta.content_full or "")
    return DocumentMetadata(
        path=meta.path,
        name=meta.name,
        mime_type=meta.mime_type,
        size_bytes=meta.size_bytes,
        created_at=meta.created_at,
        modified_at=meta.modified_at,
        content_preview=clean_preview,
        content_full=clean_full,
        is_corrupt=meta.is_corrupt,
        document_subtype=meta.document_subtype,
        author=meta.author,
        title=meta.title,
    )
