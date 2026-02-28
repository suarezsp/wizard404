"""
wizard404_core.extractors.code_binary - Código fuente y binarios (ejecutables).

Para .c, .h, .java, .py, .js, .ts, .go, .rs, .sh, .bat lee como texto.
Para .exe, .dll, .so, .dylib solo metadatos (sin contenido).
En fallo devuelve DocumentMetadata con is_corrupt=True.
"""

from datetime import datetime
from pathlib import Path

from wizard404_core.extractors.base import Extractor, register_extractor
from wizard404_core.models import DocumentMetadata

_CODE_EXTENSIONS = {".c", ".h", ".java", ".py", ".js", ".ts", ".go", ".rs", ".sh", ".bat"}
_BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib"}
_MIME_CODE = {
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
}
_MIME_BINARY = "application/octet-stream"


class CodeBinaryExtractor(Extractor):
    """Extractor para archivos de código y ejecutables (solo metadatos)."""

    supported_extensions = _CODE_EXTENSIONS | _BINARY_EXTENSIONS

    def extract(self, path: Path) -> DocumentMetadata:
        stat = path.stat()
        ext = path.suffix.lower()
        if ext in _BINARY_EXTENSIONS:
            return self._extract_binary(path, stat)
        return self._extract_code(path, stat, ext)

    def _extract_binary(self, path: Path, stat) -> DocumentMetadata:
        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type=_MIME_BINARY,
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview="",
            content_full="",
        )

    def _extract_code(self, path: Path, stat, ext: str) -> DocumentMetadata:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return DocumentMetadata(
                path=str(path.resolve()),
                name=path.name,
                mime_type=_MIME_CODE.get(ext, "text/plain"),
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                content_preview="",
                content_full="",
                is_corrupt=True,
            )
        preview = content[:500].strip() if content else ""
        return DocumentMetadata(
            path=str(path.resolve()),
            name=path.name,
            mime_type=_MIME_CODE.get(ext, "text/plain"),
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content_preview=preview,
            content_full=content,
        )


register_extractor(CodeBinaryExtractor())
