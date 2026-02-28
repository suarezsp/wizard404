"""
wizard404_cli.main - Punto de entrada de la CLI (w14).

Comandos: start/init (menú TUI), import, scan, index, search, browse.
"""

import sys
from pathlib import Path

# Añadir backend al path para importar wizard404_core
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import typer
from rich.console import Console

from wizard404_cli.commands import browse, index_cmd, import_cmd, scan, search_cmd
from wizard404_cli.tui.native_menu import run as run_native_menu

app = typer.Typer(
    name="w14",
    help="W14 - Wizard404 Document Search (menú: w14 start)",
)
console = Console()


def _run_tui() -> None:
    """Lanza el menú TUI nativo en la terminal (estilo Mole, sin Textual)."""
    run_native_menu()


app.command(name="start", help="Abre el menú interactivo en la terminal")(_run_tui)
app.command(name="init", help="Alias de start: abre el menú interactivo")(_run_tui)

app.command(name="import")(import_cmd.import_cmd)
app.command(name="scan")(scan.scan_cmd)
app.command(name="index")(index_cmd.index_cmd)
app.command(name="search")(search_cmd.search_cmd)
app.command(name="browse")(browse.browse_cmd)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Sin comando: abre el menú (como w14 start)."""
    if ctx.invoked_subcommand is None:
        _run_tui()


if __name__ == "__main__":
    app()
