"""
Comando browse.

Menu TUI tipo mole con tabla de documentos, filtros y detalle.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

try:
    import sys
    backend = Path(__file__).resolve().parent.parent.parent.parent / "backend"
    sys.path.insert(0, str(backend))
    from wizard404_core import discover_and_extract, extract_metadata
    from wizard404_core.models import DocumentMetadata
except ImportError:
    discover_and_extract = None
    extract_metadata = None
    DocumentMetadata = None


def get_documents_in_path(path: str, recursive: bool = False) -> list:
    """Devuelve la lista de DocumentMetadata del path, sin imprimir nada. recursive=False = solo directorio actual."""
    if DocumentMetadata is None or discover_and_extract is None:
        return []
    p = Path(path).resolve()
    if not p.exists():
        return []
    return list(discover_and_extract(p, recursive=recursive))


def run_browse(path: str) -> bool:
    """Lista documentos y pide número para ver detalle. Devuelve True si OK."""
    p = Path(path).resolve()
    if not p.exists():
        console.print(f"[red]Does not exist: {path}[/red]")
        return False
    if discover_and_extract is None:
        console.print("[yellow]Backend no disponible.[/yellow]")
        return False
    docs = list(discover_and_extract(p))
    if not docs:
        console.print("[yellow]No supported documents found.[/yellow]")
        return True
    table = Table(
        title=f"[bold cyan]Documents in[/bold cyan] {path}",
        title_style="bold",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Path", style="dim", max_width=30)
    for i, d in enumerate(docs, 1):
        table.add_row(
            str(i),
            d.name,
            d.mime_type,
            f"{d.size_bytes:,}",
            d.path[-30:] if len(d.path) > 30 else d.path,
        )
    console.print(table)
    choice = Prompt.ask("Select number to view detail (or Enter to exit)", default="")
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(docs):
            doc = docs[idx - 1]
            panel = Panel(
                doc.content_preview or "(no extractable content)",
                title=f"[bold]{doc.name}[/bold]",
                subtitle=f"{doc.mime_type} | {doc.size_bytes:,} bytes",
                border_style="cyan",
            )
            console.print(panel)
        else:
            console.print("[red]Invalid number.[/red]")
    else:
        console.print("[dim]Exiting...[/dim]")
    return True


def browse_cmd(
    path: str = typer.Argument(".", help="Directory to explore"),
):
    """Explora documentos en modo TUI (tabla + detalle)."""
    if not run_browse(path):
        raise typer.Exit(1)
