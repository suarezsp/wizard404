"""
Menú Explore: navegar árbol y ver detalle de archivos.
"""

from pathlib import Path
from simple_term_menu import TerminalMenu

from wizard404_cli.tui import common as tui_common
from wizard404_cli.tui.common import (
    core_available,
    show_file_detail,
    format_tree_entry,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STATUS_SUBMENU,
    BROWSE_TREE_CONFIRM_FILES,
)


def run_browse_tree(initial_path: str) -> None:
    """Navegación por árbol: menú con subdirectorios y archivos del directorio actual."""
    if not core_available():
        console = tui_common.get_console()
        console.print("[yellow]Backend not available for exploration.[/yellow]")
        input("\n  [Enter] Back to menu")
        return

    list_subdirectories = tui_common.list_subdirectories
    list_files_in_directory = tui_common.list_files_in_directory
    extract_metadata = tui_common.extract_metadata
    console = tui_common.get_console()

    if not list_subdirectories or not list_files_in_directory or not extract_metadata:
        console.print("[yellow]Backend not available for exploration.[/yellow]")
        input("\n  [Enter] Back to menu")
        return

    root_path = Path(initial_path).resolve()
    if not root_path.is_dir():
        console.print("[red]Invalid directory.[/red]")
        input("\n  [Enter] Back to menu")
        return

    current_path = root_path

    while True:
        subdirs = list_subdirectories(current_path)
        files = list_files_in_directory(current_path)

        if len(files) > BROWSE_TREE_CONFIRM_FILES:
            r = input(f"  There are {len(files)} files in this directory. Continue? (Y/N): ").strip().upper()
            if r != "Y":
                if current_path == root_path:
                    return
                current_path = current_path.parent
                continue

        options: list[tuple[str, str, object]] = []
        if current_path != root_path:
            options.append(("↑ Parent directory", "parent", None))
        for d in subdirs:
            label = format_tree_entry(f"/ {d.name}", d.name.startswith("."))
            options.append((label, "dir", d))
        for f in files:
            label = format_tree_entry(f.name, f.name.startswith("."))
            options.append((label, "file", f))
        options.append(("← Back", "back", None))

        menu = TerminalMenu(
            [o[0] for o in options],
            title=f"\n  Explore: {current_path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        idx = menu.show()
        if idx is None or options[idx][1] == "back":
            return

        kind = options[idx][1]
        value = options[idx][2]

        if kind == "parent":
            current_path = current_path.parent
        elif kind == "dir":
            current_path = value
        elif kind == "file":
            doc = extract_metadata(value)
            if doc:
                show_file_detail(doc)
            else:
                console.print("[yellow]Could not read metadata of the file.[/yellow]")
            input("\n  [Enter] Continue")


def handle_explore() -> None:
    path = tui_common.pick_directory_tree("  Choose directory to explore", confirm_label="Explore this directory")
    if path:
        run_browse_tree(path)
