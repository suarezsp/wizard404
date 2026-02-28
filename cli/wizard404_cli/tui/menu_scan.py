"""
Menú Scan: elegir directorio, ejecutar scan y mostrar resultados por tipo/directorio.
Una sola pasada con discover_and_extract; resultados en memoria para Summary y opciones sin re-escanear.
"""

from datetime import datetime, timedelta
from pathlib import Path

from simple_term_menu import TerminalMenu
from rich.prompt import Prompt
from rich.table import Table

from wizard404_cli.tui.common import (
    STATUS_SUBMENU,
    MENU_HIGHLIGHT_STYLE,
    STATUS_BAR_STYLE,
    STYLE_INFO,
    DELIMITER_LINE,
    ask_filter_selection,
    ask_filter_values,
    pick_directory_tree,
    run_list_detail_loop,
    core_available,
    get_console,
)
from wizard404_cli.tui.loading import run_with_loading_scan

from wizard404_cli.tui import common as tui_common

# Old = not modified in 2+ months
OLD_DAYS_THRESHOLD = 60


def _build_stats_from_metadata(metas: list, DirectoryStats) -> "DirectoryStats":
    """Build DirectoryStats from a list of DocumentMetadata."""
    stats = DirectoryStats()
    for m in metas:
        stats.total_files += 1
        stats.total_size += m.size_bytes
        ext = m.extension
        stats.by_extension[ext] = stats.by_extension.get(ext, 0) + 1
        stats.by_type[m.mime_type] = stats.by_type.get(m.mime_type, 0) + 1
    return stats


def _do_scan_with_cache(path: str):
    """Single pass: discover_and_extract, build stats, return (path, stats, list of metadata)."""
    if not tui_common.discover_and_extract or tui_common.DirectoryStats is None:
        return (path, None, [])
    metas = list(tui_common.discover_and_extract(path, recursive=True))
    stats = _build_stats_from_metadata(metas, tui_common.DirectoryStats)
    return (path, stats, metas)


def _show_summary_table(path: str, stats, cached_metadata_list: list) -> None:
    """Show Summary table: extension, count, size, old, new; plus entropy message."""
    console = get_console()
    if not stats or not cached_metadata_list:
        console.print("[yellow]No data to summarize.[/yellow]")
        return
    # Per-extension: count, total size, old count (modified > 2 months ago), new count
    threshold = datetime.now() - timedelta(days=OLD_DAYS_THRESHOLD)
    ext_data = {}
    for m in cached_metadata_list:
        ext = m.extension
        if ext not in ext_data:
            ext_data[ext] = {"count": 0, "size": 0, "old": 0, "new": 0}
        ext_data[ext]["count"] += 1
        ext_data[ext]["size"] += m.size_bytes
        if m.modified_at is None:
            ext_data[ext]["old"] += 1
        elif m.modified_at < threshold:
            ext_data[ext]["old"] += 1
        else:
            ext_data[ext]["new"] += 1
    table = Table(
        title=f"Summary — {path}",
        title_style="bold cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Extension", style="green")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Old", justify="right", style="dim")
    table.add_column("New", justify="right", style="cyan")
    for ext in sorted(ext_data.keys()):
        d = ext_data[ext]
        table.add_row(ext, str(d["count"]), f"{d['size']:,}", str(d["old"]), str(d["new"]))
    console.print(table)
    if tui_common.get_entropy_message:
        msg = tui_common.get_entropy_message(stats)
        console.print(DELIMITER_LINE, style="dim")
        console.print(f"  [{STYLE_INFO}] {msg} [/]")
    input("\n  [Enter] Back to results menu")


def run_scan_results_menu(path: str, stats, cached_metadata_list: list) -> None:
    """Post-scan menu: Summary, view by file type/directory, list with filters; all from cache."""
    if not core_available():
        console = get_console()
        console.print("[yellow]Backend not available for listing files.[/yellow]")
        input("\n  [Enter] Back to menu")
        return

    scan_menu_options = [
        "Summary                       — Type, count, size, old/new + entropy",
        "View by file type             — List by extension (PDF, JPG, …)",
        "View by directory             — Navigate subdirectories",
        "List with filters             — Type, name, date, size",
        "Back to main menu",
    ]

    while True:
        menu = TerminalMenu(
            scan_menu_options,
            title=f"\n  Scan results: {path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        idx = menu.show()
        if idx is None or idx == 4:
            return

        if idx == 0:
            _show_summary_table(path, stats, cached_metadata_list)

        elif idx == 1:
            exts = sorted(stats.by_extension.keys())
            if not exts:
                console = get_console()
                console.print("[yellow]No extensions found in this scan.[/yellow]")
                input("\n  [Enter] Continue")
                continue
            ext_options = [f"{ext}  ({stats.by_extension[ext]} files)" for ext in exts]
            ext_options.append("← Back")
            ext_menu = TerminalMenu(
                ext_options,
                title="  Choose file type\n",
                clear_screen=True,
                menu_highlight_style=MENU_HIGHLIGHT_STYLE,
                status_bar_style=STATUS_BAR_STYLE,
                status_bar=STATUS_SUBMENU,
            )
            ext_idx = ext_menu.show()
            if ext_idx is None or ext_idx == len(ext_options) - 1:
                continue
            chosen_ext = exts[ext_idx]
            docs = [m for m in cached_metadata_list if m.extension == chosen_ext]
            if not docs:
                console = get_console()
                console.print("[yellow]No files with metadata found.[/yellow]")
            else:
                run_list_detail_loop(docs, f"Files {chosen_ext}", count_label="files")

        elif idx == 3:
            active = ask_filter_selection()
            if active is not None:
                filters = ask_filter_values(active)
                if filters is not None and tui_common.list_documents and cached_metadata_list:
                    try:
                        results = tui_common.list_documents(cached_metadata_list, filters)
                        docs = [r.metadata for r in results if r.metadata]
                        console = get_console()
                        if not docs:
                            console.print("[yellow]No documents matching the filters found.[/yellow]")
                        else:
                            run_list_detail_loop(docs, "List with filters", count_label="document(s)")
                    except Exception as e:
                        console = get_console()
                        console.print(f"[red]Error: {e}[/red]")
            input("\n  [Enter] Back to results menu")

        elif idx == 2:
            if not tui_common.list_subdirectories:
                continue
            subdirs = tui_common.list_subdirectories(path)
            if not subdirs:
                console = get_console()
                console.print("[yellow]No subdirectories found.[/yellow]")
                input("\n  [Enter] Continue")
                continue
            subdir_options = [f"{d.name}/  —  {d}" for d in subdirs]
            subdir_options.append("← Back")
            subdir_menu = TerminalMenu(
                subdir_options,
                title="  Choose directory\n",
                clear_screen=True,
                menu_highlight_style=MENU_HIGHLIGHT_STYLE,
                status_bar_style=STATUS_BAR_STYLE,
                status_bar=STATUS_SUBMENU,
            )
            subdir_idx = subdir_menu.show()
            if subdir_idx is None or subdir_idx == len(subdir_options) - 1:
                continue
            chosen_dir = subdirs[subdir_idx]
            chosen_resolved = Path(chosen_dir).resolve()
            docs = [m for m in cached_metadata_list if Path(m.path).resolve().parent == chosen_resolved]
            if not docs:
                console = get_console()
                console.print(f"[yellow]No supported files in {chosen_dir.name}[/yellow]")
            else:
                run_list_detail_loop(docs, f"Files in {chosen_dir.name}", count_label="files")


def handle_scan() -> None:
    """Menú Scan: one pass with discover_and_extract, then results menu (Summary, view by type/dir, filters) from cache."""
    path = pick_directory_tree("  Choose directory to scan")
    if not path:
        return
    try:
        path, stats, cached = run_with_loading_scan(_do_scan_with_cache, path)
    except Exception:
        input("\n  [Enter] Back to menu")
        return
    if stats is not None and cached is not None:
        run_scan_results_menu(path, stats, cached)
    else:
        get_console().print("[yellow]Scan produced no data.[/yellow]")
        input("\n  [Enter] Back to menu")
