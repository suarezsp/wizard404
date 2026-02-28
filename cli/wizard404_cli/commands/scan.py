"""
Comando scan.

Escanea un directorio y muestra estadisticas agregadas por tipo, size y fecha.
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
    from wizard404_core.discovery import analyze_directory
    from wizard404_core.models import DirectoryStats
except ImportError:
    analyze_directory = None
    DirectoryStats = None  # type: ignore[misc, assignment]


def run_scan(directory: str, recursive: bool = True, quiet: bool = False) -> tuple[bool, "DirectoryStats | None"]:
    """Ejecuta el escaneo y muestra resultado. Devuelve (True, stats) si OK, (False, None) si error.
    Si quiet=True (TUI), no imprime la tabla; solo devuelve el resultado."""
    p = Path(directory).resolve()
    if not p.is_dir():
        console.print(f"[red]Is not a directory: {directory}[/red]")
        return False, None
    if analyze_directory is None:
        console.print("[yellow]Backend not available.[/yellow]")
        return False, None
    stats = analyze_directory(p, recursive=recursive)
    if not quiet:
        table = Table(
            title=f"[bold cyan]Scan:[/bold cyan] {directory}",
            title_style="bold",
            header_style="bold cyan",
            show_lines=True,
        )
        table.add_column("Extensión", style="green")
        table.add_column("Cantidad", justify="right", style="yellow")
        for ext, n in sorted(stats.by_extension.items()):
            table.add_row(ext, str(n))
        table.add_row("", "")
        table.add_row("[bold]Total files[/bold]", str(stats.total_files))
        table.add_row("[bold]Total size[/bold]", f"{stats.total_size:,} bytes")
        console.print(table)
    return True, stats


def scan_cmd(
    directory: str = typer.Argument(..., help="Directory to scan"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r"),
):
    """Escanea un directorio y muestra resumen por tipo y tamaño."""
    ok, _ = run_scan(directory, recursive=recursive)
    if not ok:
        raise typer.Exit(1)
