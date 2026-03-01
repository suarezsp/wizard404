"""
Menu Search: buscar en directorio o en el indice; ver documentos indexados.
handle_index_view = redirige a la web (Explore); handle_search_index = buscar en indice; handle_search = submenu.
"""

from rich.table import Table
from rich.prompt import Prompt
from simple_term_menu import TerminalMenu

from wizard404_cli.commands import search_cmd
from wizard404_cli.api_client import get_api_config, search_indexed, TOKEN_MSG
from wizard404_cli.tui import common as tui_common
from wizard404_cli.tui.common import (
    pick_directory_tree,
    ask_search_filters,
    show_files_table,
    show_file_detail,
    run_list_detail_loop,
    display_name,
    FRONTEND_BASE_URL,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STATUS_SUBMENU,
    STYLE_ALERT,
    STYLE_ERROR,
)
from wizard404_cli.tui.loading import run_with_loading_long


def handle_search_in_directory() -> None:
    """Busca en un directorio local con filtros (tipo, tamano, etc)."""
    path = pick_directory_tree("  Search in directory", confirm_label="Search in this directory")
    if not path:
        return
    query = input("  Keywords: ").strip()
    console = tui_common.get_console()
    if not query:
        console.print("[yellow]Write a search.[/yellow]")
        input("\n  [Enter] Back to menu")
        return
    filters = ask_search_filters(query)
    if filters is None:
        input("\n  [Enter] Back to menu")
        return
    try:
        results = run_with_loading_long(
            lambda: search_cmd.run_search_with_filters(path, filters),
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        input("\n  [Enter] Back to menu")
        return
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        console.print("[dim]Try to relax filters or other keywords.[/dim]")
    else:
        while True:
            table = Table(
                title=f"Search: '{query}'",
                title_style="bold cyan",
                header_style="bold cyan",
                show_lines=True,
            )
            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Size", justify="right", style="yellow")
            table.add_column("Snippet", style="dim", max_width=40)
            for i, r in enumerate(results, 1):
                if r.metadata:
                    snip = (r.snippet[:37] + "...") if len(r.snippet) > 40 else r.snippet
                    table.add_row(
                        str(i),
                        display_name(r.metadata),
                        r.metadata.mime_type,
                        f"{r.metadata.size_bytes:,}",
                        snip,
                    )
            console.print(table)
            console.print(f"[green]Found {len(results)} result(s).[/green]")
            choice = Prompt.ask("\n  Number to view detail (or Enter to go back)", default="")
            if not choice or not choice.strip():
                break
            if choice.isdigit():
                j = int(choice)
                if 1 <= j <= len(results) and results[j - 1].metadata:
                    show_file_detail(results[j - 1].metadata)
                    sub = Prompt.ask("  [Enter] Back to list  [B] Back to menu", default="")
                    if sub.strip().upper() == "B":
                        break
                else:
                    console.print("[red]Invalid number.[/red]")


def handle_search_index() -> None:
    """Busca entre los archivos anadidos al indice (API)."""
    query = input("  Keywords: ").strip()
    console = tui_common.get_console()
    if not query:
        console.print("[yellow]Write a search.[/yellow]")
        input("\n  [Enter] Back to menu")
        return
    use_semantic = input("  Usar busqueda semantica (por significado)? (s/N): ").strip().lower() == "s"
    _, token = get_api_config()
    if not token:
        console.print(f"[{STYLE_ALERT}] {TOKEN_MSG} [/]")
        input("\n  [Enter] Back to menu")
        return
    try:
        api_results, err = run_with_loading_long(
            lambda: search_indexed(query, limit=100, semantic=use_semantic),
        )
        if err:
            console.print(f"[{STYLE_ERROR}] {err} [/]")
            input("\n  [Enter] Back to menu")
            return
        if not api_results:
            console.print("[yellow]No results found in the index.[/yellow]")
            console.print("[dim]Try other keywords or add more documents to the index.[/dim]")
            input("\n  [Enter] Back to menu")
        else:
            run_list_detail_loop(api_results, f"Search in index: '{query}'", count_label="result(s)")
    except Exception as e:
        console.print(f"[{STYLE_ERROR}] Error inesperado: {e} [/]")
        input("\n  [Enter] Back to menu")


def handle_index_view() -> None:
    """Redirige al usuario a la interfaz web para ver y gestionar documentos indexados."""
    console = tui_common.get_console()
    explore_url = f"{FRONTEND_BASE_URL.rstrip('/')}/explore"
    console.print("[bold]Documentos indexados[/bold]")
    console.print("Para ver y gestionar el indice de documentos, usa la interfaz web (Explore).")
    console.print(f"  [cyan]{explore_url}[/cyan]")
    console.print("[dim]Desde ahi puedes listar, buscar e importar archivos.[/dim]")
    input("\n  [Enter] Back to menu")


def handle_search() -> None:
    """Submenu de busqueda: tras ver index o resultados volvemos aqui, no al menu principal."""
    search_submenu = [
        "Search in a directory",
        "Search between the added files (index)",
        "Index — View indexed documents",
        "Back",
    ]
    while True:
        search_menu = TerminalMenu(
            search_submenu,
            title="\n  Where to search\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        search_choice = search_menu.show()
        if search_choice is None or search_choice == 3:
            return
        if search_choice == 0:
            handle_search_in_directory()
        elif search_choice == 1:
            handle_search_index()
        else:
            handle_index_view()
