"""
Menu TUI nativo de terminal (Wizard404).

Pantalla de inicio con ASCII art, link GitHub, tagline y version.
Navegacion con flechas/j/k; item seleccionado en morado; pie en gris oscuro.
Post-scan: menu para ver resultados por tipo de archivo o por directorio.

Orquestador: run() es el bucle principal; los handlers viven en menu_scan,
menu_search, menu_organize, menu_cleanup, menu_explore y menu_import.
"""

from simple_term_menu import TerminalMenu

from wizard404_cli.tui.common import (
    play_ascii_entrance,
    print_header_after_ascii,
    get_console,
    show_help_screen,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STATUS_MAIN,
)
from wizard404_cli.tui import menu_scan
from wizard404_cli.tui import menu_import
from wizard404_cli.tui import menu_search
from wizard404_cli.tui import menu_explore
from wizard404_cli.tui import menu_organize
from wizard404_cli.tui import menu_cleanup

MAIN_OPTIONS = [
    "Scan directory        — Analyze types and sizes",
    "Import documents      — Add files to the index",
    "Search                — Search by keywords",
    "Explore documents     — Navigate and view content",
    "Organize files        — Move into folders by type/date/size",
    "Cleanup               — Find cache, logs and tiny files",
    "Help                  — TUI usage instructions",
    "Exit",
]


def run() -> None:
    """Bucle principal del menú nativo (w404 start / w404 init)."""
    first_time = True
    console = get_console()

    while True:
        if first_time:
            play_ascii_entrance()
            print_header_after_ascii()
            first_time = False
        else:
            console.clear()
            print_header_after_ascii()

        menu = TerminalMenu(
            MAIN_OPTIONS,
            title="",
            clear_screen=False,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_MAIN,
        )
        idx = menu.show()
        if idx is None or idx == 7:  # Exit or Escape
            return
        if idx == 0:
            menu_scan.handle_scan()
        elif idx == 1:
            menu_import.handle_import()
        elif idx == 2:
            menu_search.handle_search()
        elif idx == 3:
            menu_explore.handle_explore()
        elif idx == 4:
            menu_organize.handle_organize()
        elif idx == 5:
            menu_cleanup.handle_cleanup()
        elif idx == 6:
            show_help_screen()
