"""
Descubrimiento y analisis de archivos en directorios.

Descubre archivos soportados recursivamente, obtiene metadatos y genera
estadisticas agregadas por tipo y extension.
"""

from pathlib import Path
from typing import Iterator

from wizard404_core.models import DocumentMetadata, DirectoryStats
from wizard404_core.extractors import extract_metadata

SUPPORTED_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".rst", ".log", ".csv", ".docx", ".xlsx",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif",
}

"""
Descubre archivos soportados en el path dado.
Si path es un archivo, lo devuelve si está soportado.
 """
def discover_files(
    path: str | Path,
    recursive: bool = True,
    extensions: set[str] | None = None,
) -> Iterator[Path]:
    p = Path(path).resolve()
    exts = extensions or SUPPORTED_EXTENSIONS
    if p.is_file():
        if p.suffix.lower() in exts:
            yield p
        return
    if not p.is_dir():
        return
    pattern = "**/*" if recursive else "*"
    for f in p.glob(pattern):
        if f.is_file() and f.suffix.lower() in exts:
            yield f


"""
Analiza un directorio y devuelve estadisticas agregadas.
No extrae contenido completo, solo cuenta por tipo y tamaño.
"""
def analyze_directory(path: str | Path, recursive: bool = True) -> DirectoryStats:  
    stats = DirectoryStats()
    for f in discover_files(path, recursive=recursive):
        stat = f.stat()
        stats.total_files += 1
        stats.total_size += stat.st_size
        ext = f.suffix.lower()
        stats.by_extension[ext] = stats.by_extension.get(ext, 0) + 1
        mime = _mime_for_ext(ext)
        stats.by_type[mime] = stats.by_type.get(mime, 0) + 1
    return stats

"""
Descubre archivos y extrae metadatos de cada uno.
Util para scan + preview sin persistir.
"""
def discover_and_extract(
    path: str | Path,
    recursive: bool = True,
) -> Iterator[DocumentMetadata]:
    for f in discover_files(path, recursive):
        meta = extract_metadata(f)
        if meta:
            yield meta

"""Lista archivos con la extension dada (ext debe incluir punto, ej. .pdf)."""
def list_files_by_extension(
    path: str | Path,
    ext: str,
    recursive: bool = True,
) -> list[Path]:
    exts = {ext.lower()}
    return sorted(discover_files(path, recursive=recursive, extensions=exts), key=lambda x: x.name)

"""Lista archivos de una extension y devuelve sus metadatos."""
def list_files_by_extension_with_metadata(
    path: str | Path,
    ext: str,
    recursive: bool = True,
) -> list[DocumentMetadata]:
    files = list_files_by_extension(path, ext, recursive=recursive)
    result = []
    for f in files:
        meta = extract_metadata(f)
        if meta:
            result.append(meta)
    return result

"""Lista subdirectorios directos del path, ordenados por nombre."""
def list_subdirectories(path: str | Path) -> list[Path]:
    p = Path(path).resolve()
    if not p.is_dir():
        return []
    return sorted(d for d in p.iterdir() if d.is_dir())

"""Lista archivos soportados en el directorio (sin recursión)."""
def list_files_in_directory(path: str | Path) -> list[Path]:
    return sorted(discover_files(path, recursive=False), key=lambda x: x.name)

"""Lista archivos del directorio con metadatos."""
def list_files_in_directory_with_metadata(path: str | Path) -> list[DocumentMetadata]:
    files = list_files_in_directory(path)
    result = []
    for f in files:
        meta = extract_metadata(f)
        if meta:
            result.append(meta)
    return result

"""Obtiene el MIME type para una extension."""  
def _mime_for_ext(ext: str) -> str:
    mimes = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    return mimes.get(ext, "application/octet-stream")
