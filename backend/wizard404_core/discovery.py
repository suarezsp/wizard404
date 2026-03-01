"""
Descubrimiento y analisis de archivos en directorios.

Descubre archivos soportados recursivamente, obtiene metadatos y genera
estadisticas agregadas por tipo y extension.
"""

from pathlib import Path
from typing import Iterator

from wizard404_core.models import DocumentMetadata, DirectoryStats
from wizard404_core.extractors import extract_metadata

# Tipo para resultado con resumen de fallos (scan)
DiscoverResult = tuple[list["DocumentMetadata"], int, str]

# Extensiones detectadas en scan/organize/explore (exhaustivo: documentos, codigo, config, medios)
SUPPORTED_EXTENSIONS = {
    # Documentos y texto
    ".pdf", ".txt", ".md", ".rst", ".log", ".csv", ".docx", ".xlsx",
    ".doc", ".xls", ".odt", ".ods", ".rtf", ".tex", ".sty", ".bib",
    ".mdx", ".ipynb", ".Rmd", ".qmd",
    # Imagen
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".svg", ".ico",
    # Video y audio
    ".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v", ".wmv", ".flv",
    ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".opus", ".weba",
    # Codigo y markup
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".java", ".py", ".pyw", ".pyi",
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".rb", ".php",
    ".jl", ".swift", ".kt", ".kts", ".scala", ".sc", ".r", ".R", ".sql",
    ".sh", ".bash", ".bat", ".cmd", ".ps1", ".zsh", ".fish", ".ksh",
    ".html", ".htm", ".xhtml", ".xml", ".xsl", ".xslt", ".svg",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".config",
    ".vue", ".svelte", ".astro", ".pl", ".pm", ".lua", ".rkt", ".scm",
    ".clj", ".cljs", ".cljc", ".edn", ".vim", ".gradle", ".proto",
    ".graphql", ".gql", ".coffee", ".less", ".scss", ".sass",
    ".hs", ".lhs", ".fs", ".fsi", ".fsx", ".vb", ".vbs", ".asm", ".s",
    ".nim", ".cr", ".ex", ".exs", ".eex", ".heex", ".ml", ".mli", ".re", ".rei",
    ".zig", ".v", ".sv", ".pp", ".rake", ".erb", ".haml", ".slim",
    ".mustache", ".hbs", ".ejs", ".njk", ".twig", ".j2", ".liquid",
    # Binarios
    ".exe", ".dll", ".so", ".dylib", ".a", ".lib", ".o", ".obj",
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


def discover_and_extract_with_summary(
    path: str | Path,
    recursive: bool = True,
) -> DiscoverResult:
    """
    Descubre archivos, extrae metadatos y devuelve lista + contador de fallos y mensaje breve.
    failed_count = archivos no soportados (extract_metadata devolvió None) o con error (is_corrupt).
    error_summary = texto breve para mostrar al usuario tras el scan si failed_count > 0.
    """
    metas: list[DocumentMetadata] = []
    failed_count = 0
    for f in discover_files(path, recursive):
        meta = extract_metadata(f)
        if meta:
            metas.append(meta)
            if meta.is_corrupt:
                failed_count += 1
        else:
            failed_count += 1
    error_summary = f"{failed_count} archivos no soportados o con error" if failed_count else ""
    return (metas, failed_count, error_summary)

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
        ".doc": "application/msword",
        ".xls": "application/vnd.ms-excel",
        ".odt": "application/vnd.oasis.opendocument.text",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".rtf": "application/rtf",
        ".tex": "application/x-tex",
        ".bib": "application/x-bibtex",
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
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
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
        ".opus": "audio/opus",
        ".c": "text/x-c",
        ".h": "text/x-c",
        ".cpp": "text/x-c++",
        ".hpp": "text/x-c++",
        ".java": "text/x-java-source",
        ".py": "text/x-python",
        ".pyw": "text/x-python",
        ".pyi": "text/x-python",
        ".js": "text/javascript",
        ".ts": "text/typescript",
        ".jsx": "text/jsx",
        ".tsx": "text/tsx",
        ".go": "text/x-go",
        ".rs": "text/x-rust",
        ".rb": "text/x-ruby",
        ".php": "text/x-php",
        ".jl": "text/x-julia",
        ".swift": "text/x-swift",
        ".kt": "text/x-kotlin",
        ".scala": "text/x-scala",
        ".r": "text/x-r",
        ".R": "text/x-r",
        ".sql": "application/sql",
        ".sh": "text/x-shellscript",
        ".bat": "application/x-bat",
        ".cmd": "application/x-bat",
        ".ps1": "text/x-powershell",
        ".html": "text/html",
        ".htm": "text/html",
        ".xhtml": "application/xhtml+xml",
        ".xml": "application/xml",
        ".xsl": "application/xml",
        ".xslt": "application/xml",
        ".json": "application/json",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".toml": "application/toml",
        ".ini": "text/plain",
        ".cfg": "text/plain",
        ".conf": "text/plain",
        ".vue": "text/x-vue",
        ".exe": "application/octet-stream",
        ".dll": "application/octet-stream",
        ".so": "application/octet-stream",
        ".dylib": "application/octet-stream",
    }
    return mimes.get(ext, "application/octet-stream")
