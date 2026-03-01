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

# Codigo fuente y markup leidos como texto; binarios solo metadatos
_CODE_EXTENSIONS = {
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".java", ".py", ".pyw", ".pyi", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".rb", ".php", ".jl", ".swift", ".kt", ".kts", ".scala", ".sc",
    ".r", ".R", ".sql", ".sh", ".bash", ".bat", ".cmd", ".ps1", ".zsh", ".fish", ".ksh",
    ".html", ".htm", ".xhtml", ".xml", ".xsl", ".xslt", ".svg",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".config",
    ".vue", ".svelte", ".astro", ".pl", ".pm", ".lua", ".rkt", ".scm",
    ".clj", ".cljs", ".cljc", ".edn", ".vim", ".gradle", ".proto", ".graphql", ".gql",
    ".coffee", ".less", ".scss", ".sass", ".hs", ".lhs", ".fs", ".fsi", ".fsx",
    ".vb", ".vbs", ".asm", ".s", ".nim", ".cr", ".ex", ".exs", ".eex", ".heex",
    ".ml", ".mli", ".re", ".rei", ".zig", ".v", ".sv", ".pp", ".rake",
    ".erb", ".haml", ".slim", ".mustache", ".hbs", ".ejs", ".njk", ".twig", ".j2", ".liquid",
    ".mdx", ".ipynb", ".Rmd", ".qmd", ".tex", ".sty", ".bib",
}
_BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".a", ".lib", ".o", ".obj"}
_MIME_CODE = {
    ".c": "text/x-c", ".h": "text/x-c", ".cpp": "text/x-c++", ".hpp": "text/x-c++",
    ".java": "text/x-java-source", ".py": "text/x-python", ".pyw": "text/x-python", ".pyi": "text/x-python",
    ".js": "text/javascript", ".ts": "text/typescript", ".jsx": "text/jsx", ".tsx": "text/tsx",
    ".mjs": "text/javascript", ".cjs": "text/javascript",
    ".go": "text/x-go", ".rs": "text/x-rust", ".rb": "text/x-ruby", ".php": "text/x-php",
    ".jl": "text/x-julia", ".swift": "text/x-swift", ".kt": "text/x-kotlin", ".kts": "text/x-kotlin",
    ".scala": "text/x-scala", ".sc": "text/x-scala", ".r": "text/x-r", ".R": "text/x-r",
    ".sql": "application/sql", ".sh": "text/x-shellscript", ".bat": "application/x-bat",
    ".cmd": "application/x-bat", ".ps1": "text/x-powershell",
    ".html": "text/html", ".htm": "text/html", ".xhtml": "application/xhtml+xml",
    ".xml": "application/xml", ".xsl": "application/xml", ".xslt": "application/xml",
    ".svg": "image/svg+xml", ".json": "application/json",
    ".yaml": "text/yaml", ".yml": "text/yaml", ".toml": "application/toml",
    ".ini": "text/plain", ".cfg": "text/plain", ".conf": "text/plain", ".config": "text/plain",
    ".vue": "text/x-vue", ".pl": "text/x-perl", ".pm": "text/x-perl", ".lua": "text/x-lua",
    ".vim": "text/x-vim", ".proto": "text/x-protobuf", ".graphql": "application/graphql", ".gql": "application/graphql",
    ".less": "text/x-less", ".scss": "text/x-scss", ".sass": "text/x-sass",
    ".tex": "application/x-tex", ".sty": "text/x-tex", ".bib": "application/x-bibtex",
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
