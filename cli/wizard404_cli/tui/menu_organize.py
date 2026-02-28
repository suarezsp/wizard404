"""
Menú Organize: elegir origen, destino, criterio y ejecutar movimiento.
"""

from simple_term_menu import TerminalMenu

from wizard404_cli.commands import organize_cmd
from wizard404_cli.tui import common as tui_common
from wizard404_cli.tui.common import (
    pick_directory_tree,
    parse_date,
    SEARCH_SIZE_RANGES,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STATUS_SUBMENU,
)


def handle_organize() -> None:
    console = tui_common.get_console()
    console.print("\n  [yellow]Wizard404 will create folders and move files. You choose the source and destination.[/yellow]")
    if input("  Continue? (Y/N): ").strip().upper() != "Y":
        return
    source_path = pick_directory_tree("  Choose source directory to organize", confirm_label="Organize this directory")
    if not source_path:
        return
    dest_menu = TerminalMenu(
        ["Use default (e.g. ~/Desktop/Organized)", "Choose destination folder"],
        title="\n  Destination base\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=STATUS_SUBMENU,
    )
    dest_choice = dest_menu.show()
    if dest_choice is None:
        return
    if dest_choice == 0:
        base_dest = organize_cmd.get_organize_base()
    else:
        base_dest = pick_directory_tree("  Choose destination base folder", confirm_label="Use this folder")
        if not base_dest:
            return
    criterion_menu = TerminalMenu(
        ["By file type", "By date (2-month buckets)", "By size range"],
        title="\n  Group by\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=STATUS_SUBMENU,
    )
    crit_idx = criterion_menu.show()
    if crit_idx is None:
        return
    criterion = ["type", "date", "size"][crit_idx]
    from_date = None
    date_field = "modified_at"
    if criterion == "date":
        d_from = input("  From date (DD-MM-YYYY or empty for all): ").strip()
        from_date = parse_date(d_from) if d_from else None
        if input("  Use creation (c) or modification (m) date? (c/m): ").strip().lower() == "c":
            date_field = "created_at"
    size_ranges = list(SEARCH_SIZE_RANGES) if criterion == "size" else None
    preview = organize_cmd.run_organize_preview(
        source_path, base_dest, criterion,
        from_date=from_date, size_ranges=size_ranges, date_field=date_field,
    )
    if not preview:
        input("\n  [Enter] Back to menu")
        return
    organize_cmd.print_preview(preview)
    if input("  Create these folders and move files? (Y/N): ").strip().upper() != "Y":
        input("\n  [Enter] Back to menu")
        return
    if organize_cmd.run_organize_execute(preview):
        console.print("[green]Done![/green]")
    else:
        console.print("[red]Some operations failed.[/red]")
    input("\n  [Enter] Back to menu")
