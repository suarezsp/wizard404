"""
Organize: move files into folders by type, date or size.

Creates folders under a base path (default ~/Desktop/Organized or
~/.config/w404/organize_base) and moves supported files with user confirmation.
"""

from pathlib import Path
from datetime import datetime
import shutil

import typer
from rich.console import Console
from rich.table import Table

console = Console()

# Default base when no config is set
DEFAULT_ORGANIZE_BASE = str(Path.home() / "Desktop" / "Organized")
CONFIG_ORGANIZE_BASE_FILE = Path.home() / ".config" / "w404" / "organize_base"

try:
    import sys
    _backend = Path(__file__).resolve().parent.parent.parent.parent / "backend"
    if _backend.exists() and str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from wizard404_core.discovery import discover_and_extract
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False
    discover_and_extract = None  # type: ignore[assignment]


def get_organize_base() -> str:
    """Return the base directory for organized output (config file or default)."""
    if CONFIG_ORGANIZE_BASE_FILE.exists():
        try:
            base = CONFIG_ORGANIZE_BASE_FILE.read_text(encoding="utf-8").strip()
            if base:
                return str(Path(base).expanduser().resolve())
        except Exception:
            pass
    return str(Path(DEFAULT_ORGANIZE_BASE).expanduser().resolve())


def _ensure_core() -> bool:
    if not _CORE_AVAILABLE or discover_and_extract is None:
        console.print("[yellow]Backend (wizard404_core) not available.[/yellow]")
        return False
    return True


def _bucket_label_date(dt: datetime | None) -> str:
    """Two-month bucket label, e.g. 2024-01_2024-02."""
    if not dt:
        return "unknown"
    y, m = dt.year, dt.month
    # bucket start month: 1, 3, 5, 7, 9, 11
    start_m = ((m - 1) // 2) * 2 + 1
    end_m = start_m + 1
    end_y = y if end_m <= 12 else y + 1
    end_m = end_m if end_m <= 12 else 1
    return f"{y:04d}-{start_m:02d}_{end_y:04d}-{end_m:02d}"


def _size_range_label(size_bytes: int, size_ranges: list[tuple[str, int | None, int | None]]) -> str:
    """Return the label for the size range that contains size_bytes."""
    for label, min_b, max_b in size_ranges:
        if label == "Any" and min_b is None and max_b is None:
            return "Any"
        if min_b is not None and size_bytes < min_b:
            continue
        if max_b is not None and size_bytes > max_b:
            continue
        return label
    return "Other"


def run_organize_preview(
    source: str,
    base_dest: str,
    criterion: str,
    *,
    from_date: datetime | None = None,
    size_ranges: list[tuple[str, int | None, int | None]] | None = None,
    date_field: str = "modified_at",
) -> dict | None:
    """
    Dry-run: collect supported files from source and group by criterion.
    Returns dict with keys: subfolders (dict label -> list of file paths), total_files, total_size.
    criterion: "type" | "date" | "size"
    """
    if not _ensure_core():
        return None
    src = Path(source).resolve()
    base = Path(base_dest).expanduser().resolve()
    if not src.is_dir():
        console.print(f"[red]Not a directory: {source}[/red]")
        return None
    try:
        base.relative_to(src)
        console.print("[red]Destination must be outside the source tree.[/red]")
        return None
    except ValueError:
        pass
    try:
        src.relative_to(base)
        console.print("[red]Destination must be outside the source tree.[/red]")
        return None
    except ValueError:
        pass

    metas = list(discover_and_extract(src, recursive=True))
    if not metas:
        console.print("[yellow]No supported files found in source.[/yellow]")
        return None

    subfolders: dict[str, list[tuple[str, int]]] = {}  # label -> [(path, size), ...]

    if criterion == "type":
        for m in metas:
            ext = m.extension or ".bin"
            label = ext  # e.g. .pdf, .png
            if label not in subfolders:
                subfolders[label] = []
            subfolders[label].append((m.path, m.size_bytes))

    elif criterion == "date":
        for m in metas:
            dt = m.modified_at if date_field == "modified_at" else m.created_at
            label = _bucket_label_date(dt)
            if from_date and dt and dt < from_date:
                continue
            if label not in subfolders:
                subfolders[label] = []
            subfolders[label].append((m.path, m.size_bytes))

    elif criterion == "size" and size_ranges:
        for m in metas:
            label = _size_range_label(m.size_bytes, size_ranges)
            if label == "Any":
                label = "any"
            if label not in subfolders:
                subfolders[label] = []
            subfolders[label].append((m.path, m.size_bytes))

    else:
        console.print("[red]Invalid criterion or missing size_ranges.[/red]")
        return None

    total_files = sum(len(v) for v in subfolders.values())
    total_size = sum(s for v in subfolders.values() for _, s in v)
    return {
        "subfolders": subfolders,
        "total_files": total_files,
        "total_size": total_size,
        "base_dest": str(base),
    }


def run_organize_execute(plan: dict) -> bool:
    """
    Create folders under plan["base_dest"] and move files. plan is from run_organize_preview.
    Validates that every destination is under base_dest. Uses only shutil.move (never delete).
    """
    base = Path(plan["base_dest"]).expanduser().resolve()
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[red]Failed to create base directory {base}: {e}[/red]")
        return False
    subfolders = plan.get("subfolders") or {}
    for label, files in subfolders.items():
        # Sanitize folder name: visible names (e.g. "txt" not ".txt") so folders are not hidden on Unix/macOS
        safe_label = "".join(c for c in label if c not in "/\\")
        if safe_label.startswith(".") and len(safe_label) > 1:
            safe_label = safe_label[1:]
        if not safe_label or safe_label == "..":
            safe_label = "other"
        dest_dir = base / safe_label
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Failed to create {dest_dir}: {e}[/red]")
            return False
        for path_str, _ in files:
            src = Path(path_str).resolve()
            if not src.is_file():
                continue
            dest_file = dest_dir / src.name
            if dest_file.exists():
                stem, suf = dest_file.stem, dest_file.suffix
                n = 1
                while dest_file.exists():
                    dest_file = dest_dir / f"{stem} ({n}){suf}"
                    n += 1
            try:
                dest_resolved = dest_file.resolve()
                dest_resolved.relative_to(base)
            except ValueError:
                console.print(f"[red]Destination would be outside base: {dest_file}[/red]")
                return False
            try:
                shutil.move(str(src), str(dest_file))
            except OSError as e:
                console.print(f"[red]Failed to move {src} to {dest_file}: {e}[/red]")
                return False
    console.print(f"[dim]Files are in: {base}[/dim]")
    return True


def print_preview(preview: dict) -> None:
    """Print a Rich table with subfolder counts and sizes."""
    table = Table(
        title="Organize preview (dry-run)",
        title_style="bold cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Subfolder", style="green")
    table.add_column("Files", justify="right", style="yellow")
    table.add_column("Size", justify="right", style="cyan")
    for label, items in sorted(preview["subfolders"].items()):
        total = sum(s for _, s in items)
        table.add_row(label, str(len(items)), f"{total:,} bytes")
    table.add_row("", "", "")
    table.add_row("[bold]Total[/bold]", str(preview["total_files"]), f"{preview['total_size']:,} bytes")
    console.print(table)
    console.print(f"Destination: [cyan]{preview['base_dest']}[/cyan]")


def organize_cmd(
    source: str = typer.Argument(..., help="Source directory to organize"),
    destination: str = typer.Option(None, "--destination", "-d", help="Base destination (default: from config or ~/Desktop/Organized)"),
    by: str = typer.Option("type", "--by", "-b", help="Group by: type, date, size"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only show preview"),
):
    """Organize files into folders by type, date or size (CLI entry point)."""
    base = destination or get_organize_base()
    size_ranges = [
        ("Any", None, None),
        ("1 byte - 10 MB", 0, 10 * 1024 * 1024),
        ("10 MB - 500 MB", 10 * 1024 * 1024, 500 * 1024 * 1024),
        ("500 MB - 2 GB", 500 * 1024 * 1024, 2 * 1024**3),
        ("Greater than 2 GB", 2 * 1024**3, None),
    ]
    preview = run_organize_preview(source, base, by, size_ranges=size_ranges)
    if not preview:
        raise typer.Exit(1)
    print_preview(preview)
    if dry_run:
        return
    if not typer.confirm("Create these folders and move files?"):
        return
    if run_organize_execute(preview):
        console.print("[green]Done![/green]")
    else:
        raise typer.Exit(1)
