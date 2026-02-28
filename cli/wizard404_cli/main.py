"""
Punto de entrada de la CLI (w404).

Comandos: start/init (menu TUI), import, scan, index, search, browse, organize, cleanup.
"""

import sys
from pathlib import Path

# Añadir backend al path para importar wizard404_core
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import typer
from rich.console import Console

from wizard404_cli.commands import browse, index_cmd, import_cmd, scan, search_cmd, organize_cmd, cleanup_cmd
from wizard404_cli.tui.native_menu import run as run_native_menu
from wizard404_cli.backend_launcher import ensure_backend_and_token

app = typer.Typer(
    name="w404",
    help="W404 - Wizard404 Document Search (menu: w404 start)",
)
console = Console()


def _run_tui() -> None:
    """Lanza el menú TUI nativo en la terminal (estilo Mole, sin Textual)."""
    # Subir backend si no esta y asegurar token por defecto para Index / Search en indice
    ensure_backend_and_token()
    run_native_menu()


app.command(name="start", help="Open the interactive menu in the terminal")(_run_tui)
app.command(name="init", help="Alias of start: open the interactive menu in the terminal")(_run_tui)

app.command(name="import")(import_cmd.import_cmd)
app.command(name="scan")(scan.scan_cmd)
app.command(name="index")(index_cmd.index_cmd)
app.command(name="search")(search_cmd.search_cmd)
app.command(name="browse")(browse.browse_cmd)
app.command(name="organize")(organize_cmd.organize_cmd)
app.command(name="cleanup")(cleanup_cmd.cleanup_cmd)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Without command: open the menu (like w404 start)."""
    if ctx.invoked_subcommand is None:
        _run_tui()


if __name__ == "__main__":
    app()
