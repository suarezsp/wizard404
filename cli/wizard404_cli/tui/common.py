"""
Utilidades y constantes compartidas del TUI.

Constantes de menú, estilos, selector de directorio, tablas, filtros de búsqueda
y helpers de ASCII/versión para el menú principal.
"""

import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from simple_term_menu import TerminalMenu
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

# Asegurar backend en path para wizard404_core
_backend_path = Path(__file__).resolve().parent.parent.parent.parent / "backend"
if _backend_path.exists() and str(_backend_path) not in sys.path:
    sys.path.insert(0, str(_backend_path))

try:
    from wizard404_core import (
        discover_and_extract,
        discover_and_extract_with_summary,
        list_documents,
        list_files_by_extension_with_metadata,
        list_subdirectories,
        list_files_in_directory,
        list_files_in_directory_with_metadata,
        extract_metadata,
        get_entropy_message,
    )
    from wizard404_core.models import DirectoryStats, SearchFilters
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False
    discover_and_extract = None  # type: ignore[assignment]
    discover_and_extract_with_summary = None  # type: ignore[assignment]
    list_documents = None  # type: ignore[assignment]
    list_files_by_extension_with_metadata = None  # type: ignore[assignment]
    list_subdirectories = None  # type: ignore[assignment]
    list_files_in_directory = None  # type: ignore[assignment]
    list_files_in_directory_with_metadata = None  # type: ignore[assignment]
    extract_metadata = None  # type: ignore[assignment]
    get_entropy_message = None  # type: ignore[assignment]
    DirectoryStats = None  # type: ignore[misc, assignment]
    SearchFilters = None  # type: ignore[misc, assignment]

# Opciones de búsqueda: tipo MIME (etiqueta, valor para SearchFilters)
SEARCH_MIME_OPTIONS = [
    ("Any", None),
    ("PDF", "application/pdf"),
    ("JPEG / JPG", "image/jpeg"),
    ("PNG", "image/png"),
    ("GIF", "image/gif"),
    ("HEIC", "image/heic"),
    ("Video (MP4)", "video/mp4"),
    ("Audio (MP3)", "audio/mpeg"),
    ("Plain text", "text/plain"),
    ("Markdown", "text/markdown"),
    ("DOCX", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("XLSX", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
]
SEARCH_SIZE_RANGES = [
    ("Any", None, None),
    ("1 byte - 10 MB", 0, 10 * 1024 * 1024),
    ("10 MB - 500 MB", 10 * 1024 * 1024, 500 * 1024 * 1024),
    ("500 MB - 2 GB", 500 * 1024 * 1024, 2 * 1024**3),
    ("Greater than 2 GB", 2 * 1024**3, None),
]
FILTER_OPTIONS = ["Type", "Name", "Date", "Size"]
FILTER_TIPO, FILTER_NOMBRE, FILTER_FECHA, FILTER_PESO = 0, 1, 2, 3

_console = Console()

ASCII_INDEX = 0
NAV_HINT = "↑↓ j/k"
GITHUB_LINK = "https://github.com/suarezsp/wizard404"
TAGLINE = "Organizing your files with magic and spells. :P"
BROWSE_TREE_CONFIRM_FILES = 100
STATUS_MAIN = f"{NAV_HINT} Navigate  [Enter] Select  [Q] Exit"
STATUS_SUBMENU = f"  {NAV_HINT} Navigate   [Enter] Select   [B] or [Q] Back"

MENU_HIGHLIGHT_STYLE = ("fg_cyan", "bold")
MENU_HIGHLIGHT_STYLE_ALT = ("fg_yellow", "bold")
MENU_HIGHLIGHT_STYLE_DIR = ("fg_purple", "bold")
MENU_HIGHLIGHT_STYLE_TREE = ("fg_blue", "bold")
STATUS_BAR_STYLE = ("fg_cyan",)
TITLE_STYLE = ("bold", "fg_white")
# Alert/importance styles (backgrounds for CLI)
STYLE_ALERT = "bold on yellow"
STYLE_ERROR = "bold on red"
STYLE_INFO = "bold on blue"
DELIMITER_LINE = "=" * 60
# URL de la interfaz web (Explore / Import). Variable W404_FRONTEND_URL para override.
FRONTEND_BASE_URL = os.environ.get("W404_FRONTEND_URL", "http://localhost:5173")
WIZARD_COL_WIDTH = 20

# Texto para la pantalla Help (instrucciones de uso de la TUI)
HELP_BODY = """
Navigation
  Up/Down arrows or [j] / [k]  Move selection
  [Enter]                       Confirm selection or open
  [Q] or [B]                   Back / Exit submenu

Main menu
  Scan directory    Analyze types and sizes in a folder (local).
  Import documents  Add files to the index (requires backend).
  Search            Search by keywords in the index (requires backend).
  Explore documents Browse folders and view file metadata (local).
  Organize files    Move files into folders by type, date or size (local).
  Cleanup           Find cache, logs, tiny and duplicate files (local).

Tips
  In directory picker: navigate with arrows, [Enter] to select, [B] to go back.
  After a scan you can view results by file type or by directory.
  For index and search use the web interface: """ + FRONTEND_BASE_URL + """
"""


def show_help_screen() -> None:
    """Muestra en terminal las instrucciones de uso de la TUI. Espera Enter para volver."""
    console = get_console()
    console.print(Panel(HELP_BODY.strip(), title="[bold cyan]Wizard404 TUI — Help[/bold cyan]", border_style="cyan"))
    input("\n  [Enter] Back to menu")


def _ascii_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "ascii.txt"


def _load_ascii_blocks() -> list[str]:
    path = _ascii_path()
    if not path.exists():
        return ["Wizard404"]
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return blocks if blocks else ["Wizard404"]


def _get_ascii_rotation_index(num_blocks: int) -> int:
    """Returns current rotation index (0..num_blocks-1) and persists next index for next run."""
    if num_blocks <= 0:
        return 0
    config_dir = Path.home() / ".config" / "w404"
    index_file = config_dir / "ascii_index"
    idx = 0
    try:
        if index_file.exists():
            raw = index_file.read_text().strip()
            if raw.isdigit():
                idx = int(raw) % num_blocks
    except Exception:
        pass
    next_idx = (idx + 1) % num_blocks
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        index_file.write_text(str(next_idx))
    except Exception:
        pass
    return idx


def _wizard_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "wizard.txt"


def _load_wizard_lines() -> list[str]:
    path = _wizard_path()
    if not path.exists():
        return []
    return [line.rstrip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]


def play_ascii_entrance() -> None:
    """Print wizard (left) + rotated title block (right), then delimiter."""
    blocks = _load_ascii_blocks()
    wizard_lines = _load_wizard_lines()
    if not blocks:
        _console.print("Wizard404")
        _console.print(DELIMITER_LINE, style="dim")
        return
    num_blocks = len(blocks)
    idx = min(_get_ascii_rotation_index(num_blocks), num_blocks - 1)
    title_lines = blocks[idx].split("\n")
    max_lines = max(len(wizard_lines), len(title_lines))
    for i in range(max_lines):
        w = wizard_lines[i] if i < len(wizard_lines) else ""
        t = title_lines[i] if i < len(title_lines) else ""
        _console.print((w[: WIZARD_COL_WIDTH].ljust(WIZARD_COL_WIDTH) + t))
        sys.stdout.flush()
        time.sleep(0.06)
    _console.print(DELIMITER_LINE, style="dim")


def print_header_after_ascii() -> None:
    _console.print(GITHUB_LINK, style="bold")
    _console.print(TAGLINE)
    _console.print(get_version(), style="yellow")
    _console.print(DELIMITER_LINE, style="dim")


def _load_ascii_art() -> str:
    blocks = _load_ascii_blocks()
    if not blocks:
        return "Wizard404"
    idx = max(0, min(ASCII_INDEX, len(blocks) - 1))
    return blocks[idx]


def get_version() -> str:
    try:
        from importlib.metadata import version
        return version("wizard404-cli")
    except Exception:
        return "0.1.0"


def get_console() -> Console:
    return _console


def parse_date(s: str) -> datetime | None:
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d-%m-%Y")
    except ValueError:
        return None


def ask_filter_selection() -> list[int] | None:
    menu = TerminalMenu(
        FILTER_OPTIONS,
        title="\n  Activate filters (Space mark/unmark, Enter continue)\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=f"  [Space] mark/unmark       [Enter] Continue         {STATUS_SUBMENU.strip()}",
        multi_select=True,
        multi_select_select_on_accept=False,
        show_multi_select_hint=True,
    )
    result = menu.show()
    if result is None:
        return None
    return sorted(result) if isinstance(result, (list, tuple)) else [result]


def ask_filter_values(active_indices: list[int]) -> "SearchFilters | None":
    if not active_indices or SearchFilters is None:
        return SearchFilters(query="", limit=100) if SearchFilters else None
    mime_type = None
    name_pattern = None
    name_contains = None
    from_date = None
    to_date = None
    date_field = "modified_at"
    min_size = None
    max_size = None

    if FILTER_TIPO in active_indices:
        type_labels = [o[0] for o in SEARCH_MIME_OPTIONS]
        type_menu = TerminalMenu(
            type_labels,
            title="\n  File type\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        idx = type_menu.show()
        if idx is None:
            return None
        mime_type = SEARCH_MIME_OPTIONS[idx][1]

    if FILTER_NOMBRE in active_indices:
        nom = input("  Name: contains (c) or pattern (p)? ").strip().lower()
        if nom == "c":
            name_contains = input("  Name must contain: ").strip() or None
        elif nom == "p":
            name_pattern = input("  Pattern (e.g. *.pdf): ").strip() or None

    if FILTER_FECHA in active_indices:
        if input("  Filter by creation (c) or modification (m)? (c/m): ").strip().lower() == "c":
            date_field = "created_at"
        d_from = input("  From (DD-MM-YYYY or empty): ").strip()
        d_to = input("  To (DD-MM-YYYY or empty): ").strip()
        from_date = parse_date(d_from)
        to_date = parse_date(d_to)

    if FILTER_PESO in active_indices:
        size_labels = [r[0] for r in SEARCH_SIZE_RANGES]
        size_menu = TerminalMenu(
            size_labels,
            title="\n  Size range\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        idx = size_menu.show()
        if idx is not None:
            _, min_size, max_size = SEARCH_SIZE_RANGES[idx]

    return SearchFilters(
        query="",
        mime_type=mime_type,
        min_size=min_size,
        max_size=max_size,
        from_date=from_date,
        to_date=to_date,
        date_field=date_field,
        name_pattern=name_pattern,
        name_contains=name_contains,
        limit=100,
    )


def ask_search_filters(query: str) -> "SearchFilters | None":
    if SearchFilters is None:
        return None
    mime_type = None
    from_date = None
    to_date = None
    date_field = "modified_at"
    min_size = None
    max_size = None
    name_pattern = None
    name_contains = None

    type_labels = [o[0] for o in SEARCH_MIME_OPTIONS]
    type_menu = TerminalMenu(
        type_labels,
        title="\n  File type\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=STATUS_SUBMENU,
    )
    type_idx = type_menu.show()
    if type_idx is None:
        return None
    mime_type = SEARCH_MIME_OPTIONS[type_idx][1]

    if input("  Filter by date? (s/N): ").strip().lower() == "s":
        if input("  By creation (c) or modification (m)? (c/m): ").strip().lower() == "c":
            date_field = "created_at"
        d_from = input("  From (DD-MM-YYYY or empty): ").strip()
        d_to = input("  To (DD-MM-YYYY or empty): ").strip()
        from_date = parse_date(d_from)
        to_date = parse_date(d_to)

    size_labels = [r[0] for r in SEARCH_SIZE_RANGES]
    size_menu = TerminalMenu(
        size_labels,
        title="\n  Size range\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=STATUS_SUBMENU,
    )
    size_idx = size_menu.show()
    if size_idx is not None:
        _, min_size, max_size = SEARCH_SIZE_RANGES[size_idx]

    nom = input("  Filter by name? Contains (c) / Pattern (p) / No (n): ").strip().lower()
    if nom == "c":
        name_contains = input("  Name must contain: ").strip() or None
    elif nom == "p":
        name_pattern = input("  Pattern (e.g. pepe-*.*): ").strip() or None

    return SearchFilters(
        query=query,
        mime_type=mime_type,
        min_size=min_size,
        max_size=max_size,
        from_date=from_date,
        to_date=to_date,
        date_field=date_field,
        name_pattern=name_pattern,
        name_contains=name_contains,
        limit=100,
    )


def directory_choices() -> list[tuple[str, str | None]]:
    home = Path.home()
    choices = []
    for label, p in [
        ("Documents", home / "Documents"),
        ("Downloads", home / "Downloads"),
        ("Desktop", home / "Desktop"),
        ("Home", home),
        ("Current directory", Path.cwd()),
    ]:
        if p.exists():
            choices.append((f"{label}  —  {p}", str(p.resolve())))
    choices.append(("Write path manually...", None))
    return choices


def pick_directory(title: str) -> str | None:
    choices_with_paths = directory_choices()
    labels = [c[0] for c in choices_with_paths]
    menu = TerminalMenu(
        labels,
        title=title,
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=STATUS_SUBMENU,
    )
    idx = menu.show()
    if idx is None:
        return None
    _, path_val = choices_with_paths[idx]
    if path_val is not None:
        return path_val
    raw = input("Path (Enter = cancel): ").strip()
    return raw if raw else None


# Sufijo para marcar archivos/directorios ocultos en el arbol. No usamos codigos ANSI
# en las opciones de TerminalMenu porque desalinean el cursor y corrompen el
# redibujado (p. ej. al mover el raton).
HIDDEN_SUFFIX = "  [hidden]"


def filter_hidden_paths(paths: list, show_hidden: bool) -> list:
    """Filtra paths por nombre: si show_hidden es False, excluye los que empiezan por '.'."""
    if show_hidden:
        return list(paths)
    return [p for p in paths if not getattr(p, "name", str(p)).startswith(".")]


def format_tree_entry(display_name: str, is_hidden: bool) -> str:
    """Formatea una opcion del arbol; los ocultos llevan sufijo [hidden] (sin ANSI)."""
    if not is_hidden:
        return display_name
    return display_name + HIDDEN_SUFFIX


def pick_directory_tree(title: str, confirm_label: str = "Scan this directory") -> str | None:
    if not _CORE_AVAILABLE or list_subdirectories is None:
        return pick_directory(title)
    root_path = Path("/").resolve()
    current_path = root_path

    while True:
        subdirs = list_subdirectories(current_path)
        options: list[tuple[str, str, object]] = []
        if current_path != root_path:
            options.append(("..", "parent", None))
        for d in subdirs:
            label = format_tree_entry(f"/ {d.name}", d.name.startswith("."))
            options.append((label, "dir", d))
        options.append((confirm_label, "confirm", current_path))
        options.append(("← Back", "back", None))

        menu = TerminalMenu(
            [o[0] for o in options],
            title=f"\n  {title}\n  {current_path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE_TREE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=STATUS_SUBMENU,
        )
        idx = menu.show()
        if idx is None or options[idx][1] == "back":
            return None
        kind = options[idx][1]
        value = options[idx][2]
        if kind == "parent":
            current_path = current_path.parent
        elif kind == "dir":
            current_path = value
        elif kind == "confirm":
            return str(value)
    return None


def display_name(doc) -> str:
    name = getattr(doc, "name", str(doc))
    if getattr(doc, "is_corrupt", False):
        return f"{name}  [CORRUPT]"
    return name


def display_type(doc) -> str:
    """Type label for tables; e.g. 'application/pdf [scan]' when document_subtype is 'scan'."""
    mime = getattr(doc, "mime_type", "")
    subtype = getattr(doc, "document_subtype", None)
    if subtype:
        return f"{mime} [{subtype}]"
    return mime


def show_files_table(docs: list, title: str) -> None:
    table = Table(title=title, show_lines=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Metadata / Preview", style="dim", max_width=40)
    for i, d in enumerate(docs, 1):
        preview = (d.content_preview or "")[:40] + ("..." if len(d.content_preview or "") > 40 else "")
        table.add_row(str(i), display_name(d), display_type(d), f"{d.size_bytes:,}", preview)
    _console.print(table)


def format_dt(dt) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)


def run_list_detail_loop(items: list, title: str, count_label: str = "result(s)") -> None:
    """
    Muestra tabla de items y bucle: numero para ver detalle, Enter para salir.
    Tras ver detalle: Enter = volver a lista, B = salir al menu.
    Comentario: navegacion clara (rubrica Merlin UX).
    """
    while True:
        show_files_table(items, title)
        _console.print(f"[green]Found {len(items)} {count_label}.[/green]")
        choice = Prompt.ask("\n  Number to view detail (or Enter to go back)", default="")
        if not choice or not choice.strip():
            break
        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= len(items):
                show_file_detail(items[i - 1])
                sub = Prompt.ask("  [Enter] Back to list  [B] Back to menu", default="")
                if sub.strip().upper() == "B":
                    break
            else:
                _console.print("[red]Invalid number.[/red]")


def show_file_detail(doc) -> None:
    file_lines = [
        f"Path:      {doc.path}",
        f"Name:    {doc.name}",
        f"MIME Type: {doc.mime_type}",
        f"Size:    {doc.size_bytes:,} bytes",
        f"Created:    {format_dt(doc.created_at)}",
        f"Modified: {format_dt(doc.modified_at)}",
    ]
    body = "\n".join(file_lines)
    doc_id = getattr(doc, "id", None)
    if doc_id is not None:
        try:
            from wizard404_cli.api_client import get_document_summary
            summary, err = get_document_summary(doc_id)
            if summary and not err:
                body += "\n\n--- Summary ---\n" + summary
        except Exception:
            pass
    meta_section = doc.content_full or doc.content_preview or "(no additional metadata)"
    if meta_section.strip():
        body += "\n\n--- Metadata / EXIF / Content ---\n" + meta_section
    _console.print(Panel(body, title=doc.name, subtitle=f"{doc.mime_type} | {doc.size_bytes:,} bytes", border_style="cyan"))


def core_available() -> bool:
    return _CORE_AVAILABLE


def get_list_subdirectories():
    return list_subdirectories


def get_list_files_in_directory():
    return list_files_in_directory


def get_extract_metadata():
    return extract_metadata
