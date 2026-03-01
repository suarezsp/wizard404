"""
Menú Cleanup: analizar directorio y opcionalmente borrar cache/logs/tiny.
"""

from pathlib import Path
from simple_term_menu import TerminalMenu

from wizard404_cli.commands import cleanup_cmd
from wizard404_cli.tui import common as tui_common
from wizard404_cli.tui.common import (
    pick_directory_tree,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STATUS_SUBMENU,
)
from wizard404_cli.tui.loading import run_with_loading_long


def _size_mb_display(size_bytes: int) -> str:
    mb = size_bytes / (1024 * 1024)
    return f"{mb:.2f} MB" if mb >= 0.01 else "< 0.01 MB"


def _run_cleanup_choose_files(summary: dict) -> set[str] | None:
    to_delete: set[str] = set()
    categories = [
        ("Cache dirs / files", "cache_dirs"),
        ("Log files", "logs"),
        ("Tiny files (< 1 KB)", "tiny"),
        ("Duplicados (excl. programación)", "duplicates"),
    ]
    for title, key in categories:
        items = summary.get(key) or []
        if not items:
            continue
        options = [f"{Path(p).name}  ({_size_mb_display(s)})" for p, s in items]
        preselected = list(range(len(options)))
        menu = TerminalMenu(
            options,
            title=f"\n  {title} — Space toggle, Enter confirm (selected = will delete)\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
            multi_select=True,
            multi_select_select_on_accept=False,
            show_multi_select_hint=True,
            preselected_entries=preselected,
        )
        result = menu.show()
        if result is None:
            return None
        selected = result if isinstance(result, (list, tuple)) else [result]
        for i in selected:
            if 0 <= i < len(items):
                to_delete.add(items[i][0])
    return to_delete


def handle_cleanup() -> None:
    console = tui_common.get_console()
    path = pick_directory_tree("  Choose directory to analyze (cache, logs, tiny files)", confirm_label="Analyze this directory")
    if not path:
        return
    try:
        summary = run_with_loading_long(cleanup_cmd.analyze_cleanup, path)
        if summary:
            cleanup_cmd.print_cleanup_summary(summary)
            cleanup_actions = ["Delete all", "Choose files to delete...", "Back"]
            cleanup_menu = TerminalMenu(
                cleanup_actions,
                title="\n  Cleanup\n",
                clear_screen=True,
                menu_highlight_style=MENU_HIGHLIGHT_STYLE,
                status_bar_style=STATUS_BAR_STYLE,
                status_bar=STATUS_SUBMENU,
            )
            action_idx = cleanup_menu.show()
            if action_idx == 0:
                if input("  Confirm: delete all listed items? (Y/N): ").strip().upper() == "Y":
                    ok = cleanup_cmd.run_cleanup_delete(summary)
                    if ok:
                        console.print("[green]Cleanup done.[/green]")
                    else:
                        console.print("[red]Some deletions failed.[/red]")
            elif action_idx == 1:
                to_delete = _run_cleanup_choose_files(summary)
                if to_delete is not None and len(to_delete) > 0:
                    if input(f"  Confirm: delete {len(to_delete)} selected item(s)? (Y/N): ").strip().upper() == "Y":
                        ok = cleanup_cmd.run_cleanup_delete(summary, only_paths=to_delete)
                        if ok:
                            console.print("[green]Cleanup done.[/green]")
                        else:
                            console.print("[red]Some deletions failed.[/red]")
                elif to_delete is not None:
                    console.print("[yellow]No items selected.[/yellow]")
        else:
            console.print("[yellow]Nothing to clean in this directory.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    input("\n  [Enter] Back to menu")
