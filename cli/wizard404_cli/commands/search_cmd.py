"""
Comando search.

Busca documentos por palabras clave y filtros.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

try:
    import sys
    backend = Path(__file__).resolve().parent.parent.parent.parent / "backend"
    sys.path.insert(0, str(backend))
    from wizard404_core import discover_and_extract, search_documents
    from wizard404_core.models import SearchFilters, SearchResult
except ImportError:
    discover_and_extract = None
    search_documents = None
    SearchFilters = None
    SearchResult = None


def run_search_with_filters(path: str, filters: "SearchFilters") -> list:
    """Ejecuta búsqueda con filtros y devuelve lista de SearchResult (sin imprimir). Para TUI."""
    if search_documents is None or not Path(path).exists():
        return []
    metas = list(discover_and_extract(Path(path)))
    return search_documents(metas, filters)


def run_search(query: str, path: str, limit: int = 20) -> bool:
    """Ejecuta búsqueda en un directorio y muestra resultados. Devuelve True si OK."""
    if search_documents is None:
        console.print("[yellow]Backend not available.[/yellow]")
        return False
    p = Path(path)
    if not p.exists():
        console.print(f"[red]Does not exist: {path}[/red]")
        return False
    metas = list(discover_and_extract(p))
    filters = SearchFilters(query=query, mime_type=None, limit=limit)
    results = search_documents(metas, filters)
    table = Table(title=f"Search: '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Size", justify="right")
    table.add_column("Snippet", style="dim", max_width=40)
    for r in results[:limit]:
        if r.metadata:
            snippet = (r.snippet[:37] + "...") if len(r.snippet) > 40 else r.snippet
            table.add_row(
                r.metadata.name,
                r.metadata.mime_type,
                f"{r.metadata.size_bytes:,}",
                snippet,
            )
    console.print(table)
    console.print(f"[green]{len(results)} document(s)[/green]")
    return True


def search_cmd(
    query: str = typer.Argument(..., help="Keywords"),
    path: str | None = typer.Option(None, "--path", "-p", help="Filter by directory"),
    mime_type: str | None = typer.Option(None, "--type", "-t"),
    limit: int = typer.Option(20, "--limit", "-n"),
):
    """Busca documentos por palabras clave."""
    if search_documents is None:
        console.print("[yellow]Backend not available.[/yellow]")
        raise typer.Exit(1)
    if path:
        if not run_search(query, path, limit=limit):
            raise typer.Exit(1)
    else:
        console.print("[yellow]Indicate --path to search in a local directory.[/yellow]")
        console.print("[dim]To search in the API, use GET /documents/search[/dim]")
