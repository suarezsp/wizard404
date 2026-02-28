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
    ".heic", ".heif",
    ".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v", ".wmv", ".flv",
    ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma",
    ".c", ".h", ".java", ".py", ".js", ".ts", ".go", ".rs", ".sh", ".bat",
    ".exe", ".dll", ".so", ".dylib",
}

def discover_files(
    path: str | Path,
    recursive: bool = True,
    extensions: set[str] | None = None,
) -> Iterator[Path]:
    """Descubre archivos soportados en el path; si es archivo lo devuelve si está soportado. Con recursive recorre subdirectorios."""
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


def analyze_directory(path: str | Path, recursive: bool = True) -> DirectoryStats:
    """Analiza un directorio y devuelve estadísticas agregadas (total_files, total_size, by_type, by_extension). No extrae contenido."""
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

def discover_and_extract(
    path: str | Path,
    recursive: bool = True,
) -> Iterator[DocumentMetadata]:
    """Descubre archivos soportados y extrae metadatos de cada uno; útil para scan o preview sin persistir en DB."""
    for f in discover_files(path, recursive):
        meta = extract_metadata(f)
        if meta:
            yield meta

def list_files_by_extension(
    path: str | Path,
    ext: str,
    recursive: bool = True,
) -> list[Path]:
    """Lista archivos con la extensión dada (ext debe incluir punto, ej. .pdf), ordenados por nombre."""
    exts = {ext.lower()}
    return sorted(discover_files(path, recursive=recursive, extensions=exts), key=lambda x: x.name)

def list_files_by_extension_with_metadata(
    path: str | Path,
    ext: str,
    recursive: bool = True,
) -> list[DocumentMetadata]:
    """Lista archivos de una extensión y devuelve sus metadatos extraídos (DocumentMetadata)."""
    files = list_files_by_extension(path, ext, recursive=recursive)
    result = []
    for f in files:
        meta = extract_metadata(f)
        if meta:
            result.append(meta)
    return result

def list_subdirectories(path: str | Path) -> list[Path]:
    """Lista subdirectorios directos del path, ordenados por nombre; devuelve lista vacía si no es directorio."""
    p = Path(path).resolve()
    if not p.is_dir():
        return []
    return sorted(d for d in p.iterdir() if d.is_dir())

def list_files_in_directory(path: str | Path) -> list[Path]:
    """Lista archivos soportados en el directorio (sin recursión), ordenados por nombre."""
    return sorted(discover_files(path, recursive=False), key=lambda x: x.name)

def list_files_in_directory_with_metadata(path: str | Path) -> list[DocumentMetadata]:
    """Lista archivos del directorio (sin recursión) con sus metadatos extraídos."""
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
        ".rst": "text/x-rst",
        ".log": "text/plain",
        ".csv": "text/csv",
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
        ".c": "text/x-c",
        ".h": "text/x-c",
        ".java": "text/x-java-source",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".ts": "text/typescript",
        ".go": "text/x-go",
        ".rs": "text/x-rust",
        ".sh": "text/x-shellscript",
        ".bat": "application/x-bat",
        ".exe": "application/octet-stream",
        ".dll": "application/octet-stream",
        ".so": "application/octet-stream",
        ".dylib": "application/octet-stream",
    }
    return mimes.get(ext, "application/octet-stream")
