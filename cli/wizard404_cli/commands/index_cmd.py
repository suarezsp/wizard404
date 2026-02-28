"""
Comando index.

Indexa documentos en la base de datos.
Requiere conexion a la API o a la DB.
"""

import typer
from rich.console import Console

console = Console()


def index_cmd(
    path: str = typer.Argument(..., help="File or directory to index"),
):
    """Indexa documentos (registra en la base de datos)."""
    console.print("[dim]Indexing: use POST /documents/import with the API.[/dim]")
    console.print(f"  Path: {path}")
    console.print("[yellow]To index via API, authenticate and call the import endpoint.[/yellow]")
