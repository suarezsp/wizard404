"""
Comando import.

Importa archivos o directorios. En modo API, envia a la API.
En modo local, usa wizard404_core + DB directa (requiere backend).
"""

from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console

console = Console()

# Intentar importar del backend
try:
    import sys
    backend = Path(__file__).resolve().parent.parent.parent.parent / "backend"  # /backend
    sys.path.insert(0, str(backend))
    from wizard404_core import discover_and_extract, extract_metadata, apply_filters
    from wizard404_core.models import SearchFilters
except ImportError:
    discover_and_extract = None
    extract_metadata = None
    apply_filters = None  # type: ignore[assignment]
    SearchFilters = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    from wizard404_core.models import SearchFilters as SearchFiltersType


def run_import_collect(
    path: str,
    recursive: bool = True,
    filters: "SearchFiltersType | None" = None,
) -> dict[str, int]:
    """Recorre documentos en la ruta y devuelve conteo por extensión (sin imprimir). Si filters no es None, solo cuenta los que pasan el filtro."""
    result: dict[str, int] = {}
    p = Path(path).resolve()
    if not p.exists() or discover_and_extract is None:
        return result
    if p.is_file():
        meta = extract_metadata(p)
        if meta:
            if filters and apply_filters:
                filtered = apply_filters([meta], filters)
                if not filtered:
                    return result
            ext = Path(meta.path).suffix.upper() or ".*"
            if ext.startswith("."):
                ext = ext[1:]
            result[ext] = result.get(ext, 0) + 1
        return result
    metas = list(discover_and_extract(p, recursive=recursive))
    if filters and apply_filters:
        metas = apply_filters(metas, filters)
    for meta in metas:
        ext = Path(meta.path).suffix.upper() or ".*"
        if ext.startswith("."):
            ext = ext[1:]
        result[ext] = result.get(ext, 0) + 1
    return result


def run_import(path: str, recursive: bool = True) -> bool:
    """Lista/importa documentos desde una ruta. Devuelve True si OK."""
    p = Path(path).resolve()
    if not p.exists():
        console.print(f"[red]Does not exist: {path}[/red]")
        return False
    if discover_and_extract is None:
        console.print("[yellow]Backend not available. Execute from project directory.[/yellow]")
        return False
    count = 0
    if p.is_file():
        meta = extract_metadata(p)
        if meta:
            console.print(f"[green]Found: {meta.name}[/green] ({meta.mime_type})")
            count = 1
        else:
            console.print(f"[red]Unsupported format: {p.suffix}[/red]")
    else:
        for meta in discover_and_extract(p, recursive=recursive):
            console.print(f"  {meta.name} ({meta.mime_type}, {meta.size_bytes} bytes)")
            count += 1
    console.print(f"[green]Total: {count} document(s)[/green]")
    console.print("[dim]To persist in the API, use the POST /documents/import endpoint[/dim] :D")
    return True


def import_cmd(
    path: str = typer.Argument(..., help="Path to file or directory"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r"),
):
    """Importa documentos desde una ruta."""
    if not run_import(path, recursive=recursive):
        raise typer.Exit(1)
