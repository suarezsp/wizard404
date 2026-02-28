"""
Comando index.

Indexa documentos en la API (POST /documents/import).
Usa el token de config (W404_TOKEN o ~/.config/w404/token).
"""

from pathlib import Path

import typer
from rich.console import Console

from wizard404_cli.api_client import import_to_index, get_api_config

console = Console()


def index_cmd(
    path: str = typer.Argument(..., help="File or directory to index"),
):
    """Indexa documentos en la API (archivo o directorio). Requiere backend corriendo y token configurado."""
    p = Path(path).resolve()
    if not p.exists():
        console.print(f"[red]Path does not exist: {path}[/red]")
        raise typer.Exit(1)
    base_url, token = get_api_config()
    if not token:
        console.print("[yellow]No token. Run w404 start once to auto-configure, or set W404_TOKEN.[/yellow]")
        raise typer.Exit(1)
    count, err = import_to_index(str(p))
    if err:
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Indexed {count} document(s).[/green]")
