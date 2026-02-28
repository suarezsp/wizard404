"""
Mensajes de "casos de interés" para resultados de scan (entropía del directorio).

Genera frases en inglés que indican si el directorio está ordenado o desordenado,
para guiar al usuario (ej. recomendar organizar).
"""

from wizard404_core.models import DirectoryStats

# High entropy: many extensions, few files per type. Low: few extensions, many files per type.
ENTROPY_EXTENSION_THRESHOLD = 12  # more than this many extensions → consider disorder
ENTROPY_FILES_PER_EXT_MIN = 8     # if total_files / num_extensions < this → high entropy


def get_entropy_message(stats: DirectoryStats) -> str:
    """
    Returns a short English message about directory order/disorder based on stats.
    High entropy (many extension types, scattered files) → recommend organizing.
    Low entropy (few types, concentrated) → "All in order. Very clean."
    """
    if not stats or stats.total_files == 0:
        return "Empty directory. Nothing to organize."
    num_ext = len(stats.by_extension)
    if num_ext == 0:
        return "No recognized file types."
    files_per_ext = stats.total_files / num_ext
    if num_ext > ENTROPY_EXTENSION_THRESHOLD and files_per_ext < ENTROPY_FILES_PER_EXT_MIN:
        return "High entropy... lots of disorder... recommend organizing."
    return "All in order. Very clean."
