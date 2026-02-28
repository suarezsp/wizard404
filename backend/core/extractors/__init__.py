"""
wizard404_core.extractors - Extractores de texto y metadatos por tipo de archivo.

Cada extractor implementa la interfaz base y maneja un tipo MIME específico.
La importación de los módulos concretos registra los extractores.
"""

from wizard404_core.extractors.base import Extractor, extract_metadata

# Importar para registrar extractores
import wizard404_core.extractors.text  # noqa: F401
import wizard404_core.extractors.pdf_extractor  # noqa: F401
import wizard404_core.extractors.office  # noqa: F401
import wizard404_core.extractors.image  # noqa: F401

from wizard404_core.extractors.text import TextExtractor
from wizard404_core.extractors.pdf_extractor import PDFExtractor
from wizard404_core.extractors.office import OfficeExtractor
from wizard404_core.extractors.image import ImageExtractor

__all__ = [
    "Extractor",
    "extract_metadata",
    "TextExtractor",
    "PDFExtractor",
    "OfficeExtractor",
    "ImageExtractor",
]
