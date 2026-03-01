"""
Menú Import: elegir directorio, filtros e importar al índice.
"""

from wizard404_cli.commands import import_cmd
from wizard404_cli.tui import common as tui_common
from wizard404_cli.tui.common import (
    pick_directory_tree,
    ask_filter_selection,
    ask_filter_values,
    FRONTEND_BASE_URL,
)
from wizard404_cli.tui.loading import run_with_import_loading


def handle_import() -> None:
    console = tui_common.get_console()
    import_url = f"{FRONTEND_BASE_URL.rstrip('/')}/import"
    console.print("[dim]Tip: You can also import and manage documents in the web app:[/dim]")
    console.print(f"  [cyan]{import_url}[/cyan]\n")
    path = pick_directory_tree("  Choose directory to import", confirm_label="Import from this directory")
    if not path:
        return
    active = ask_filter_selection()
    if active is None:
        input("\n  [Enter] Back to menu")
        return
    filters = ask_filter_values(active)
    if filters is None:
        input("\n  [Enter] Back to menu")
        return
    try:
        by_ext = run_with_import_loading(
            lambda: import_cmd.run_import_collect(path, True, filters),
        )
        if by_ext:
            summary = " | ".join(f"{ext}: {n}" for ext, n in sorted(by_ext.items()))
            console.print(summary, style="cyan")
            console.print("[dim]Para guardar estos documentos en el índice, use la opción 'Index' del menú (o w404 index <ruta>) con el backend corriendo.[/dim]")
        else:
            console.print("[yellow]No documents found or the path is invalid.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    input("\n  [Enter] Back to menu")
