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
    from wizard404_core import discover_and_extract, search_documents, semantic_search_documents
    from wizard404_core.models import SearchFilters, SearchResult
except ImportError:
    discover_and_extract = None
    search_documents = None
    semantic_search_documents = None
    SearchFilters = None
    SearchResult = None


def run_search_with_filters(path: str, filters: "SearchFilters", semantic: bool = False) -> list:
    """Ejecuta búsqueda con filtros y devuelve lista de SearchResult (sin imprimir). Para TUI."""
    if search_documents is None or not Path(path).exists():
        return []
    metas = list(discover_and_extract(Path(path)))
    fn = semantic_search_documents if (semantic and semantic_search_documents) else search_documents
    return fn(metas, filters)


def run_search(query: str, path: str, limit: int = 20, semantic: bool = False) -> bool:
    """Ejecuta búsqueda en un directorio y muestra resultados. semantic=True usa expansión de consulta."""
    if search_documents is None:
        console.print("[yellow]Backend not available.[/yellow]")
        return False
    p = Path(path)
    if not p.exists():
        console.print(f"[red]Does not exist: {path}[/red]")
        return False
    metas = list(discover_and_extract(p))
    filters = SearchFilters(query=query, mime_type=None, limit=limit)
    fn = semantic_search_documents if (semantic and semantic_search_documents) else search_documents
    results = fn(metas, filters)
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
    path: str | None = typer.Option(None, "--path", "-p", help="Directory to search in (local)"),
    semantic: bool = typer.Option(False, "--semantic", "-s", help="Use semantic query expansion"),
    mime_type: str | None = typer.Option(None, "--type", "-t"),
    limit: int = typer.Option(20, "--limit", "-n"),
):
    """Busca documentos por palabras clave. Con --path busca en directorio local; sin --path busca en el índice (API)."""
    if search_documents is None and not path:
        console.print("[yellow]Backend not available.[/yellow]")
        raise typer.Exit(1)
    if path:
        if not run_search(query, path, limit=limit, semantic=semantic):
            raise typer.Exit(1)
    else:
        from wizard404_cli.api_client import search_indexed, get_api_config, TOKEN_MSG

        _, token = get_api_config()
        if not token:
            console.print(f"[yellow]{TOKEN_MSG}[/yellow]")
            raise typer.Exit(1)
        results, err = search_indexed(query, semantic=semantic, limit=limit)
        if err:
            console.print(f"[red]{err}[/red]")
            raise typer.Exit(1)
        for r in results:
            console.print(f"  [cyan]{r.name}[/cyan]  {r.mime_type}  {r.size_bytes:,}  {r.content_preview[:50]}...")
        console.print(f"[green]{len(results)} document(s)[/green]")
