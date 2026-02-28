"""
Menu TUI nativo de terminal (Wizard404).

Pantalla de inicio con ASCII art, link GitHub, tagline y version.
Navegacion con flechas/j/k; item seleccionado en morado; pie en gris oscuro.
Post-scan: menu para ver resultados por tipo de archivo o por directorio.
"""

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

from wizard404_cli.api_client import get_api_config, search_indexed
from wizard404_cli.commands import scan, import_cmd, search_cmd
from wizard404_cli.tui.loading import run_with_loading_long, run_with_import_loading

# Asegurar backend en path para wizard404_core (por si se ejecuta sin main)
_backend_path = Path(__file__).resolve().parent.parent.parent.parent / "backend"
if _backend_path.exists() and str(_backend_path) not in sys.path:
    sys.path.insert(0, str(_backend_path))

try:
    from wizard404_core import (
        discover_and_extract,
        list_documents,
        list_files_by_extension_with_metadata,
        list_subdirectories,
        list_files_in_directory,
        list_files_in_directory_with_metadata,
        extract_metadata,
    )
    from wizard404_core.models import DirectoryStats, SearchFilters
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False
    discover_and_extract = None  # type: ignore[assignment]
    list_documents = None  # type: ignore[assignment]
    list_subdirectories = None  # type: ignore[assignment]
    list_files_in_directory = None  # type: ignore[assignment]
    extract_metadata = None  # type: ignore[assignment]
    DirectoryStats = None  # type: ignore[misc, assignment]
    SearchFilters = None  # type: ignore[misc, assignment]

# Opciones de búsqueda: tipo MIME (etiqueta, valor para SearchFilters)
SEARCH_MIME_OPTIONS = [
    ("Any", None),
    ("PDF", "application/pdf"),
    ("JPEG / JPG", "image/jpeg"),
    ("PNG", "image/png"),
    ("GIF", "image/gif"),
    ("Plain text", "text/plain"),
    ("Markdown", "text/markdown"),
    ("DOCX", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("XLSX", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
]
# Rangos de tamaño: (etiqueta, min_bytes, max_bytes)
SEARCH_SIZE_RANGES = [
    ("Any", None, None),
    ("1 byte - 10 MB", 0, 10 * 1024 * 1024),
    ("10 MB - 500 MB", 10 * 1024 * 1024, 500 * 1024 * 1024),
    ("500 MB - 2 GB", 500 * 1024 * 1024, 2 * 1024**3),
    ("Greater than 2 GB", 2 * 1024**3, None),
]
# Índices para menú de filtros: 0=Tipo, 1=Nombre, 2=Fecha, 3=Peso
FILTER_OPTIONS = ["Type", "Name", "Date", "Size"]
FILTER_TIPO, FILTER_NOMBRE, FILTER_FECHA, FILTER_PESO = 0, 1, 2, 3

_console = Console()


# --- Constantes (fácil de cambiar en código) ---
ASCII_INDEX = 0  # 0, 1 o 2 para elegir uno de los 3 ASCII de cli/ascii.txt
NAV_HINT = "↑↓ j/k"
GITHUB_LINK = "https://github.com/suarezsp/wizard404"
TAGLINE = f"Organizing your files with magic and spells. :P"
BROWSE_TREE_CONFIRM_FILES = 100  # Confirmar si hay más de N archivos en un directorio
BOLD = "\033[1m"
NORM = "\033[0m"

# Estilos del menú principal (colores y negrita)
MENU_HIGHLIGHT_STYLE = ("fg_cyan", "bold")
MENU_HIGHLIGHT_STYLE_ALT = ("fg_yellow", "bold")
# Selector de directorio (Escanear): ítem seleccionado en morado+negrita; sin ANSI en texto para alinear cursor
MENU_HIGHLIGHT_STYLE_DIR = ("fg_purple", "bold")
STATUS_BAR_STYLE = ("fg_cyan",)
TITLE_STYLE = ("bold", "fg_white")

# Opciones del menú principal (texto claro para ítems)
MAIN_OPTIONS = [
    "Scan directory        — Analyze types and sizes",
    "Import documents      — Add files to the index",
    "Search                — Search by keywords",
    "Explore documents     — Navigate and view content",
    "Exit",
]


def _ascii_path() -> Path:
    """Ruta a cli/ascii.txt (desde este modulo: tui -> wizard404_cli -> cli)."""
    return Path(__file__).resolve().parent.parent.parent / "ascii.txt"


def _load_ascii_blocks() -> list[str]:
    """Carga los 3 bloques ASCII de cli/ascii.txt. Devuelve lista de hasta 3 bloques."""
    path = _ascii_path()
    if not path.exists():
        return ["Wizard404"]
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        return ["Wizard404"]
    return blocks


def _get_ascii_rotation_index() -> int:
    """indice rotatorio 0..2: lee/escribe ~/.config/w14/ascii_index."""
    config_dir = Path.home() / ".config" / "w14"
    index_file = config_dir / "ascii_index"
    idx = 0
    try:
        if index_file.exists():
            raw = index_file.read_text().strip()
            if raw.isdigit():
                idx = int(raw) % 3
    except Exception:
        pass
    next_idx = (idx + 1) % 3
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        index_file.write_text(str(next_idx))
    except Exception:
        pass
    return idx


def _play_ascii_entrance() -> None:
    """Imprime el ASCII elegido (rotacion) linea a línea con animacion; no imprime link/tagline/version."""
    blocks = _load_ascii_blocks()
    if not blocks:
        _console.print("Wizard404")
        return
    idx = min(_get_ascii_rotation_index(), len(blocks) - 1)
    block = blocks[idx]
    for line in block.split("\n"):
        _console.print(line)
        sys.stdout.flush()
        time.sleep(0.06)


def _print_header_after_ascii() -> None:
    """Imprime link en negrita, tagline normal y versión en amarillo (Rich)."""
    _console.print(GITHUB_LINK, style="bold")
    _console.print(TAGLINE)
    _console.print(_get_version(), style="yellow")


def _load_ascii_art() -> str:
    """Carga uno de los 3 bloques ASCII de cli/ascii.txt (segun ASCII_INDEX)."""
    blocks = _load_ascii_blocks()
    if not blocks:
        return "Wizard404"
    idx = max(0, min(ASCII_INDEX, len(blocks) - 1))
    return blocks[idx]


def _get_version() -> str:
    """Version del paquete wizard404-cli o fallback."""
    try:
        from importlib.metadata import version
        return version("wizard404-cli")
    except Exception:
        return "0.1.0"


def _build_title() -> str:
    """Título multilínea: ASCII + link + tagline + versión."""
    parts = [
        _load_ascii_art(),
        GITHUB_LINK,
        TAGLINE,
        _get_version(),
    ]
    return "\n".join(parts)


def _parse_date(s: str) -> datetime | None:
    """Parsea DD-MM-YYYY; devuelve None si vacío o inválido."""
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d-%m-%Y")
    except ValueError:
        return None


def _ask_filter_selection() -> list[int] | None:
    """Menu multi-select para elegir filtros (Type, Name, Date, Size). Devuelve lista de indices activos o None."""
    menu = TerminalMenu(
        FILTER_OPTIONS,
        title="\n  Activate filters (Space mark/unmark, Enter continue)\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=f"  [Space] mark/unmark       [Enter] Continue         [Q] Back to menu",
        multi_select=True,
        multi_select_select_on_accept=False,
        show_multi_select_hint=True,
    )
    result = menu.show()
    if result is None:
        return None
    return sorted(result) if isinstance(result, (list, tuple)) else [result]


def _ask_filter_values(active_indices: list[int]) -> "SearchFilters | None":
    """Pide los valores de cada filtro activo en orden (Tipo, Nombre, Fecha, Peso). Devuelve SearchFilters con query=''."""
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
            title="\n  Tipo de archivo\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Continue",
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
        from_date = _parse_date(d_from)
        to_date = _parse_date(d_to)

    if FILTER_PESO in active_indices:
        size_labels = [r[0] for r in SEARCH_SIZE_RANGES]
        size_menu = TerminalMenu(
            size_labels,
            title="\n  Size range\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Continue",
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


def _ask_search_filters(query: str) -> "SearchFilters | None":
    """Menús para tipo, fecha, tamaño y nombre; devuelve SearchFilters o None si cancelar."""
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

    # Tipo
    type_labels = [o[0] for o in SEARCH_MIME_OPTIONS]
    type_menu = TerminalMenu(
        type_labels,
        title="\n  File type\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Continue",
    )
    type_idx = type_menu.show()
    if type_idx is None:
        return None
    mime_type = SEARCH_MIME_OPTIONS[type_idx][1]

    # Fecha
    if input("  Filter by date? (s/N): ").strip().lower() == "s":
        if input("  By creation (c) or modification (m)? (c/m): ").strip().lower() == "c":
            date_field = "created_at"
        d_from = input("  From (DD-MM-YYYY or empty): ").strip()
        d_to = input("  To (DD-MM-YYYY or empty): ").strip()
        from_date = _parse_date(d_from)
        to_date = _parse_date(d_to)

    # Tamaño
    size_labels = [r[0] for r in SEARCH_SIZE_RANGES]
    size_menu = TerminalMenu(
        size_labels,
        title="\n  Size range\n",
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Continue",
    )
    size_idx = size_menu.show()
    if size_idx is not None:
        _, min_size, max_size = SEARCH_SIZE_RANGES[size_idx]

    # Nombre
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


def _directory_choices() -> list[tuple[str, str | None]]:
    """Opciones de directorio: (etiqueta, path o None = escribir a mano)."""
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


def _pick_directory(title: str) -> str | None:
    """Muestra menú de directorios. Devuelve path o None si cancelar."""
    choices_with_paths = _directory_choices()
    labels = [c[0] for c in choices_with_paths]
    menu = TerminalMenu(
        labels,
        title=title,
        clear_screen=True,
        menu_highlight_style=MENU_HIGHLIGHT_STYLE,
        status_bar_style=STATUS_BAR_STYLE,
        status_bar=f"{NAV_HINT} Navigate  [Enter] Select  [Q] Cancel",
    )
    idx = menu.show()
    if idx is None:
        return None
    _, path_val = choices_with_paths[idx]
    if path_val is not None:
        return path_val
    raw = input("Path (Enter = cancel): ").strip()
    return raw if raw else None


def _pick_directory_tree(title: str, confirm_label: str = "Scan this directory") -> str | None:
    """Navega por árbol desde la raíz del sistema (/ en Linux/Mac); tipo ls con .. para subir. Devuelve path o None."""
    if not _CORE_AVAILABLE or list_subdirectories is None:
        return _pick_directory(title)
    # Raíz del sistema: / en Linux/Mac; en Windows Path("/").resolve() suele dar la unidad actual
    root_path = Path("/").resolve()
    current_path = root_path
    status_bar = f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Back"

    while True:
        subdirs = list_subdirectories(current_path)
        options: list[tuple[str, str, object]] = []
        if current_path != root_path:
            options.append(("..", "parent", None))
        for d in subdirs:
            options.append((f"/ {d.name}", "dir", d))
        options.append((confirm_label, "confirm", current_path))
        options.append(("← Back", "back", None))

        menu = TerminalMenu(
            [o[0] for o in options],
            title=f"\n  {title}\n  {current_path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE_DIR,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=status_bar,
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


def _show_files_table(docs: list, title: str) -> None:
    """Muestra una tabla Rich con lista de documentos (nombre, tipo, tamaño, preview)."""
    table = Table(title=title, show_lines=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Metadata / Preview", style="dim", max_width=40)
    for i, d in enumerate(docs, 1):
        preview = (d.content_preview or "")[:40] + ("..." if len(d.content_preview or "") > 40 else "")
        table.add_row(str(i), d.name, d.mime_type, f"{d.size_bytes:,}", preview)
    _console.print(table)


def _format_dt(dt) -> str:
    """Formatea datetime para mostrar en detalle."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)


def _show_file_detail(doc) -> None:
    """Muestra todos los metadatos del documento: campos fijos y sección EXIF/contenido."""
    # Bloque 1: campos fijos de DocumentMetadata
    file_lines = [
        f"Path:      {doc.path}",
        f"Name:    {doc.name}",
        f"MIME Type: {doc.mime_type}",
        f"Size:    {doc.size_bytes:,} bytes",
        f"Created:    {_format_dt(doc.created_at)}",
        f"Modified: {_format_dt(doc.modified_at)}",
    ]
    body = "\n".join(file_lines)
    # Bloque 2: metadatos específicos / EXIF / contenido
    meta_section = doc.content_full or doc.content_preview or "(no additional metadata)"
    if meta_section.strip():
        body += "\n\n--- Metadata / EXIF / Content ---\n" + meta_section
    _console.print(Panel(body, title=doc.name, subtitle=f"{doc.mime_type} | {doc.size_bytes:,} bytes", border_style="cyan"))


def run_browse_tree(initial_path: str) -> None:
    """Navigation tree: menu with subdirectories and files of the current directory. Only current directory (no recursive)."""
    if not _CORE_AVAILABLE or list_files_in_directory is None or extract_metadata is None:
        _console.print("[yellow]Backend not available for exploration.[/yellow]")
        input("\n  [Enter] Back to menu")
        return

    from pathlib import Path as P
    root_path = P(initial_path).resolve()
    if not root_path.is_dir():
        _console.print("[red]Invalid directory.[/red]")
        input("\n  [Enter] Back to menu")
        return

    current_path = root_path
    status_bar = f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Back"

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
            options.append((f"/ {d.name}", "dir", d))
        for f in files:
            options.append((f.name, "file", f))
        options.append(("← Back", "back", None))

        menu = TerminalMenu(
            [o[0] for o in options],
            title=f"\n  Explore: {current_path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=status_bar,
        )
        idx = menu.show()
        if idx is None or idx == len(options) - 1:
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
                _show_file_detail(doc)
            else:
                _console.print("[yellow]Could not read metadata of the file.[/yellow]")
            input("\n  [Enter] Continue")


def run_scan_results_menu(path: str, stats: "DirectoryStats") -> None:
    """Post-scan menu: view by file type or by directory."""
    if not _CORE_AVAILABLE:
        _console.print("[yellow]Backend not available for listing files.[/yellow]")
        input("\n  [Enter] Back to menu")
        return

    scan_menu_options = [
        "View by file type           — List by extension (PDF, JPG, …)",
        "View by directory           — Navigate subdirectories",
        "List with filters           — Type, name, date, size",
        "Back to main menu",
    ]
    status_bar = f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Back"

    while True:
        menu = TerminalMenu(
            scan_menu_options,
            title=f"\n  Scan results: {path}\n",
            clear_screen=True,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=status_bar,
        )
        idx = menu.show()
        if idx is None or idx == 3:
            return

        if idx == 0:  # Por tipo
            exts = sorted(stats.by_extension.keys())
            if not exts:
                _console.print("[yellow]No extensions found in this scan.[/yellow]")
                input("\n  [Enter] Continue")
                continue
            ext_options = [f"{ext}  ({stats.by_extension[ext]} archivos)" for ext in exts]
            ext_options.append("← Back")
            ext_menu = TerminalMenu(
                ext_options,
                title="  Choose file type\n",
                clear_screen=True,
                menu_highlight_style=MENU_HIGHLIGHT_STYLE,
                status_bar_style=STATUS_BAR_STYLE,
                status_bar=status_bar,
            )
            ext_idx = ext_menu.show()
            if ext_idx is None or ext_idx == len(ext_options) - 1:
                continue
            chosen_ext = exts[ext_idx]
            docs = run_with_loading_long(list_files_by_extension_with_metadata, path, chosen_ext, True)
            if not docs:
                _console.print("[yellow]No files with metadata found.[/yellow]")
            else:
                _show_files_table(docs, f"Files {chosen_ext}")
                choice = Prompt.ask("\n  Number to view detail (or Enter to back)", default="")
                if choice.isdigit():
                    i = int(choice)
                    if 1 <= i <= len(docs):
                        _show_file_detail(docs[i - 1])
                        input("\n  [Enter] Continue")
            input("\n  [Enter] Back to results menu")

        elif idx == 2:  # Listar con filtros
            active = _ask_filter_selection()
            if active is not None:
                filters = _ask_filter_values(active)
                if filters is not None and discover_and_extract is not None and list_documents is not None:
                    def _list_with_filters() -> list:
                        metas = list(discover_and_extract(path, recursive=True))
                        results = list_documents(metas, filters)
                        return [r.metadata for r in results if r.metadata]
                    try:
                        docs = run_with_loading_long(_list_with_filters)
                        if not docs:
                            _console.print("[yellow]No documents matching the filters found.[/yellow]")
                        else:
                            _show_files_table(docs, "List with filters")
                            choice = Prompt.ask("\n  Number to view detail (or Enter to back)", default="")
                            if choice.isdigit():
                                i = int(choice)
                                if 1 <= i <= len(docs):
                                    _show_file_detail(docs[i - 1])
                                    input("\n  [Enter] Continue")
                    except Exception as e:
                        _console.print(f"[red]Error: {e}[/red]")
            input("\n  [Enter] Back to results menu")

        elif idx == 1:  # Por directorio
            subdirs = list_subdirectories(path)
            if not subdirs:
                _console.print("[yellow]No subdirectories found.[/yellow]")
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
                status_bar=status_bar,
            )
            subdir_idx = subdir_menu.show()
            if subdir_idx is None or subdir_idx == len(subdir_options) - 1:
                continue
            chosen_dir = subdirs[subdir_idx]
            docs = run_with_loading_long(list_files_in_directory_with_metadata, chosen_dir)
            if not docs:
                _console.print(f"[yellow]No supported files in {chosen_dir.name}[/yellow]")
            else:
                _show_files_table(docs, f"Files in {chosen_dir.name}")
                choice = Prompt.ask("\n  Number to view detail (or Enter to back)", default="")
                if choice.isdigit():
                    i = int(choice)
                    if 1 <= i <= len(docs):
                        _show_file_detail(docs[i - 1])
                        input("\n  [Enter] Continue")
            input("\n  [Enter] Back to results menu")


def run() -> None:
    """Bucle principal del menú nativo (w14 start / w14 init)."""
    status_bar = f"{NAV_HINT} Navigate  [Enter] Select  [Q] Exit"
    first_time = True

    while True:
        if first_time:
            _play_ascii_entrance()
            _print_header_after_ascii()
            first_time = False
        else:
            _console.clear()
            _print_header_after_ascii()

        menu = TerminalMenu(
            MAIN_OPTIONS,
            title="",
            clear_screen=False,
            menu_highlight_style=MENU_HIGHLIGHT_STYLE,
            status_bar_style=STATUS_BAR_STYLE,
            status_bar=status_bar,
        )
        idx = menu.show()
        if idx is None or idx == 4:  # Salir o Escape
            return

        if idx == 0:  # Escanear
            path = _pick_directory_tree("  Choose directory to scan")
            if path:
                ok, stats = run_with_loading_long(scan.run_scan, path)
                if ok and stats:
                    run_scan_results_menu(path, stats)
                else:
                    input("\n  [Enter] Back to menu")

        elif idx == 1:  # Importar
            path = _pick_directory("  Choose directory to import")
            if path:
                active = _ask_filter_selection()
                if active is None:
                    input("\n  [Enter] Back to menu")
                else:
                    filters = _ask_filter_values(active)
                    if filters is None:
                        input("\n  [Enter] Back to menu")
                    else:
                        try:
                            by_ext = run_with_import_loading(
                                lambda: import_cmd.run_import_collect(path, True, filters),
                            )
                            if by_ext:
                                summary = " | ".join(f"{ext}: {n}" for ext, n in sorted(by_ext.items()))
                                _console.print(summary, style="cyan")
                            else:
                                _console.print("[yellow]No documents found or the path is invalid.[/yellow]")
                        except Exception as e:
                            _console.print(f"[red]Error: {e}[/red]")
                        input("\n  [Enter] Back to menu")

        elif idx == 2:  # Buscar
            search_submenu = [
                "Search in a directory",
                "Search between the added files (index)",
                "Back",
            ]
            search_menu = TerminalMenu(
                search_submenu,
                title="\n  Where to search\n",
                clear_screen=True,
                menu_highlight_style=MENU_HIGHLIGHT_STYLE,
                status_bar_style=STATUS_BAR_STYLE,
                status_bar=f"  {NAV_HINT} Navigate   [Enter] Select   [Q] Back",
            )
            search_choice = search_menu.show()
            if search_choice is None or search_choice == 2:
                continue
            if search_choice == 0:  # En directorio
                path = _pick_directory("  Search in directory")
                if path:
                    query = input("  Keywords: ").strip()
                    if not query:
                        _console.print("[yellow]Write a search.[/yellow]")
                        input("\n  [Enter] Back to menu")
                        continue
                    filters = _ask_search_filters(query)
                    if filters is None:
                        input("\n  [Enter] Back to menu")
                        continue
                    try:
                        results = run_with_loading_long(
                            lambda: search_cmd.run_search_with_filters(path, filters),
                        )
                    except Exception as e:
                        _console.print(f"[red]Error: {e}[/red]")
                        input("\n  [Enter] Back to menu")
                        continue
                    if not results:
                        _console.print("[yellow]No results found.[/yellow]")
                        _console.print("[dim]Try to relax filters or other keywords.[/dim]")
                    else:
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
                                    r.metadata.name,
                                    r.metadata.mime_type,
                                    f"{r.metadata.size_bytes:,}",
                                    snip,
                                )
                        _console.print(table)
                        _console.print(f"[green]Found {len(results)} result(s).[/green]")
                        choice = Prompt.ask("\n  Number to view detail (or Enter to back)", default="")
                        if choice.isdigit():
                            j = int(choice)
                            if 1 <= j <= len(results) and results[j - 1].metadata:
                                _show_file_detail(results[j - 1].metadata)
                                input("\n  [Enter] Continue")
                    input("\n  [Enter] Back to menu")
            else:  # search_choice == 1: En índice
                query = input("  Keywords: ").strip()
                if not query:
                    _console.print("[yellow]Write a search.[/yellow]")
                    input("\n  [Enter] Back to menu")
                    continue
                base_url, token = get_api_config()
                if not base_url or not token:
                    _console.print("[yellow]Configure W14_API_URL and W14_TOKEN and have the backend running.[/yellow]")
                    _console.print("[dim]The index uses references (paths) to imported documents, not copies.[/dim]")
                    input("\n  [Enter] Back to menu")
                    continue
                api_results = search_indexed(query, limit=100)
                if not api_results:
                    _console.print("[yellow]No results found in the index.[/yellow]")
                    _console.print("[dim]Check the URL and the token, or that there are indexed documents.[/dim]")
                else:
                    _show_files_table(api_results, f"Search in index: '{query}'")
                    _console.print(f"[green]Found {len(api_results)} result(s).[/green]")
                    choice = Prompt.ask("\n  Number to view detail (or Enter to back)", default="")
                    if choice.isdigit():
                        j = int(choice)
                        if 1 <= j <= len(api_results):
                            _show_file_detail(api_results[j - 1])
                            input("\n  [Enter] Continue")
                input("\n  [Enter] Back to menu")

        elif idx == 3:  # Explorar
            path = _pick_directory_tree("  Choose directory to explore", confirm_label="Explore this directory")
            if path:
                run_browse_tree(path)
