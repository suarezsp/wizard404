"""
Cleanup: find cache, logs and tiny files; show summary and optionally delete.

Only deletes within the user-chosen directory. Excludes system paths and
critical extensions. Requires double confirmation.
"""

import os
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

# Tiny file threshold (bytes)
TINY_THRESHOLD = 1024  # 1 KB

# Extensions we never delete (even if tiny)
NEVER_DELETE_EXTENSIONS = {".py", ".js", ".ts", ".sqlite", ".db", ".env", ".yml", ".yaml", ".json", ".xml", ".config"}

# Dir names treated as cache (only these get rmtree when user confirms)
CACHE_DIR_NAMES = {"__pycache__", ".cache", ".pytest_cache", "node_modules"}

# File/dir names that are safe to list as "cache" for deletion
CACHE_FILE_PATTERNS = (".DS_Store", ".pyc")

# Paths we never touch (system)
FORBIDDEN_PREFIXES = ("/etc", "/usr", "/System", "/Library", "/opt/homebrew/Cellar")


def _is_safe_path(root: Path, path: Path) -> bool:
    """Ensure path is under root and not a system path."""
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    p = str(path.resolve())
    for prefix in FORBIDDEN_PREFIXES:
        if p.startswith(prefix):
            return False
    return True


def _dir_size(path: Path) -> int:
    """Total size of files in directory (recursive)."""
    total = 0
    try:
        for f in path.rglob("*"):
            if f.is_file():
                try:
                    total += f.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def analyze_cleanup(directory: str) -> dict | None:
    """
    Scan directory for tiny files, cache dirs and log files. No deletion.
    Returns dict with keys: tiny, cache_dirs, logs, total_reclaimable, root.
    """
    root = Path(directory).resolve()
    if not root.is_dir():
        console.print(f"[red]Not a directory: {directory}[/red]")
        return None
    if not _is_safe_path(root, root):
        console.print("[red]Directory is not allowed (system path).[/red]")
        return None

    tiny: list[tuple[str, int]] = []
    cache_dirs: list[tuple[str, int]] = []
    logs: list[tuple[str, int]] = []

    try:
        for entry in root.rglob("*"):
            if not _is_safe_path(root, entry):
                continue
            try:
                if entry.is_file():
                    size = entry.stat().st_size
                    name = entry.name.lower()
                    # Tiny files: < 1 KB, exclude critical extensions
                    if size < TINY_THRESHOLD:
                        if entry.suffix.lower() not in NEVER_DELETE_EXTENSIONS:
                            tiny.append((str(entry), size))
                    # Logs
                    elif name.endswith(".log"):
                        logs.append((str(entry), size))
                    # Cache-like files
                    elif name == ".ds_store" or name.endswith(".pyc"):
                        cache_dirs.append((str(entry), size))  # stored as "cache" file
                elif entry.is_dir():
                    if entry.name in CACHE_DIR_NAMES:
                        sz = _dir_size(entry)
                        cache_dirs.append((str(entry), sz))
            except OSError:
                continue
    except OSError as e:
        console.print(f"[red]Scan error: {e}[/red]")
        return None

    total = sum(s for _, s in tiny) + sum(s for _, s in cache_dirs) + sum(s for _, s in logs)
    return {
        "tiny": tiny,
        "cache_dirs": cache_dirs,
        "logs": logs,
        "total_reclaimable": total,
        "root": str(root),
    }


def _size_mb(size_bytes: int) -> str:
    """Format size in MB; use '< 0.01 MB' for very small values."""
    mb = size_bytes / (1024 * 1024)
    if mb < 0.01 and size_bytes > 0:
        return "< 0.01 MB"
    return f"{mb:.2f} MB"


def print_cleanup_summary(summary: dict) -> None:
    """Print Rich table with counts and sizes per category (sizes in MB)."""
    table = Table(
        title="Cleanup summary",
        title_style="bold cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Category", style="green")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Size", justify="right", style="cyan")
    n_tiny = len(summary["tiny"])
    s_tiny = sum(s for _, s in summary["tiny"])
    n_cache = len(summary["cache_dirs"])
    s_cache = sum(s for _, s in summary["cache_dirs"])
    n_logs = len(summary["logs"])
    s_logs = sum(s for _, s in summary["logs"])
    table.add_row("Tiny files (< 1 KB)", str(n_tiny), _size_mb(s_tiny))
    table.add_row("Cache dirs / files", str(n_cache), _size_mb(s_cache))
    table.add_row("Log files", str(n_logs), _size_mb(s_logs))
    table.add_row("", "", "")
    table.add_row("[bold]Total reclaimable[/bold]", str(n_tiny + n_cache + n_logs), _size_mb(summary["total_reclaimable"]))
    console.print(table)
    console.print(f"Scope: [cyan]{summary['root']}[/cyan]")


def run_cleanup_delete(summary: dict, only_paths: set[str] | None = None) -> bool:
    """
    Delete only paths listed in summary that are under summary["root"].
    If only_paths is given, delete only those paths; otherwise delete all in summary.
    Uses os.remove for files and shutil.rmtree only for known cache dir names.
    """
    root = Path(summary["root"]).resolve()
    ok = True

    def should_delete(path_str: str) -> bool:
        if only_paths is None:
            return True
        return path_str in only_paths

    for path_str, _ in summary["tiny"]:
        if not should_delete(path_str):
            continue
        p = Path(path_str).resolve()
        if not _is_safe_path(root, p) or not p.is_file():
            continue
        try:
            os.remove(p)
        except OSError as e:
            console.print(f"[red]Failed to remove {p}: {e}[/red]")
            ok = False
    for path_str, _ in summary["logs"]:
        if not should_delete(path_str):
            continue
        p = Path(path_str).resolve()
        if not _is_safe_path(root, p) or not p.is_file():
            continue
        try:
            os.remove(p)
        except OSError as e:
            console.print(f"[red]Failed to remove {p}: {e}[/red]")
            ok = False
    for path_str, _ in summary["cache_dirs"]:
        if not should_delete(path_str):
            continue
        p = Path(path_str).resolve()
        if not _is_safe_path(root, p):
            continue
        if p.is_file():
            try:
                os.remove(p)
            except OSError as e:
                console.print(f"[red]Failed to remove {p}: {e}[/red]")
                ok = False
        elif p.is_dir() and p.name in CACHE_DIR_NAMES:
            try:
                shutil.rmtree(p)
            except OSError as e:
                console.print(f"[red]Failed to remove dir {p}: {e}[/red]")
                ok = False
    return ok


def cleanup_cmd(
    directory: str = typer.Argument(..., help="Directory to analyze for cache, logs and tiny files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only show summary, do not delete"),
) -> None:
    """Find cache, logs and tiny files; show summary and optionally delete (CLI entry point)."""
    summary = analyze_cleanup(directory)
    if not summary:
        raise typer.Exit(1)
    print_cleanup_summary(summary)
    if dry_run:
        return
    if typer.confirm("Delete these items?"):
        if typer.confirm("Confirm deletion?"):
            if run_cleanup_delete(summary):
                console.print("[green]Done.[/green]")
            else:
                raise typer.Exit(1)
