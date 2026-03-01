"""
Cleanup: find cache, logs, tiny files and duplicates; show summary and optionally delete.

Only deletes within the user-chosen directory. Excludes system paths and
critical extensions. Duplicate detection excludes programming/config files.
Requires user to see and select what to delete.
"""

import hashlib
import os
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

# Tiny file threshold (bytes)
TINY_THRESHOLD = 1024  # 1 KB

# Max file size to hash for duplicate detection (bytes)
DUPLICATE_HASH_MAX_SIZE = 2 * 1024 * 1024  # 2 MB

# Extensions we never delete (even if tiny or duplicate)
NEVER_DELETE_EXTENSIONS = {".py", ".js", ".ts", ".sqlite", ".db", ".env", ".yml", ".yaml", ".json", ".xml", ".config"}

# Extensions to exclude from duplicate detection (programming/config)
DUPLICATE_EXCLUDE_EXTENSIONS = NEVER_DELETE_EXTENSIONS | {".c", ".h", ".java", ".go", ".rs", ".sh", ".bat"}

# Dir names treated as cache (only these get rmtree when user confirms)
CACHE_DIR_NAMES = {"__pycache__", ".cache", ".pytest_cache", "node_modules", "cache", "tmp", "temp", ".tmp", ".temp"}

# File/dir names that are safe to list as "cache" for deletion
CACHE_FILE_PATTERNS = (".ds_store", ".pyc", ".cache")

# Log file patterns: extension or name contains
LOG_EXTENSIONS = (".log",)
LOG_NAME_CONTAINS = ("log",)

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


def _file_md5(path: Path, max_size: int = DUPLICATE_HASH_MAX_SIZE) -> str | None:
    """MD5 del archivo (hasta max_size bytes). None si error o archivo vacío."""
    try:
        size = path.stat().st_size
        if size == 0:
            return ""
        with open(path, "rb") as f:
            data = f.read(max_size)
        return hashlib.md5(data).hexdigest()
    except OSError:
        return None


def _is_log_file(name: str) -> bool:
    """True si el nombre/extension indica archivo de log."""
    n = name.lower()
    if n.endswith(".log") or ".log." in n:
        return True
    for ext in LOG_EXTENSIONS:
        if ext in n:
            return True
    for part in LOG_NAME_CONTAINS:
        if part in n and any(n.endswith(e) for e in (".log", ".txt", ".out")):
            return True
    return False


def _is_cache_file_or_dir(entry: Path) -> bool:
    """True si es archivo o directorio de caché."""
    name = entry.name.lower()
    if entry.is_dir():
        return name in CACHE_DIR_NAMES or name in ("cache", "tmp", "temp")
    return (
        name == ".ds_store"
        or name.endswith(".pyc")
        or name.endswith(".cache")
        or name in (p.lower() for p in CACHE_FILE_PATTERNS)
    )


def analyze_cleanup(directory: str) -> dict | None:
    """
    Scan directory for tiny files, cache dirs, log files and duplicates. No deletion.
    Returns dict with keys: tiny, cache_dirs, logs, duplicates, total_reclaimable, root.
    Duplicates exclude programming/config extensions.
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
    # Candidates for duplicate detection: (path_str, size)
    duplicate_candidates: list[tuple[str, int]] = []

    try:
        for entry in root.rglob("*"):
            if not _is_safe_path(root, entry):
                continue
            try:
                if entry.is_file():
                    size = entry.stat().st_size
                    name = entry.name.lower()
                    ext = entry.suffix.lower()
                    # Tiny files: < 1 KB, exclude critical extensions
                    if size < TINY_THRESHOLD:
                        if ext not in NEVER_DELETE_EXTENSIONS:
                            tiny.append((str(entry), size))
                    # Logs: .log, .log.*, nombres que indiquen log
                    elif _is_log_file(entry.name):
                        logs.append((str(entry), size))
                    # Cache-like files and dirs
                    elif _is_cache_file_or_dir(entry):
                        if entry.is_dir():
                            sz = _dir_size(entry)
                            cache_dirs.append((str(entry), sz))
                        else:
                            cache_dirs.append((str(entry), size))
                    # Candidate for duplicate (exclude code/config)
                    if ext not in DUPLICATE_EXCLUDE_EXTENSIONS and size <= DUPLICATE_HASH_MAX_SIZE:
                        duplicate_candidates.append((str(entry), size))
                elif entry.is_dir():
                    if entry.name.lower() in {d.lower() for d in CACHE_DIR_NAMES}:
                        sz = _dir_size(entry)
                        cache_dirs.append((str(entry), sz))
            except OSError:
                continue
    except OSError as e:
        console.print(f"[red]Scan error: {e}[/red]")
        return None

    # Duplicate detection: group by (size, md5)
    duplicates: list[tuple[str, int]] = []
    size_hash_to_paths: dict[tuple[int, str], list[tuple[str, int]]] = {}
    for path_str, size in duplicate_candidates:
        p = Path(path_str)
        if not p.is_file():
            continue
        h = _file_md5(p, DUPLICATE_HASH_MAX_SIZE)
        if h is None:
            continue
        key = (size, h)
        if key not in size_hash_to_paths:
            size_hash_to_paths[key] = []
        size_hash_to_paths[key].append((path_str, size))

    duplicate_reclaimable = 0
    for key, group in size_hash_to_paths.items():
        if len(group) > 1:
            # All copies listed so user can select which to delete
            for path_str, size in group:
                duplicates.append((path_str, size))
            duplicate_reclaimable += (len(group) - 1) * group[0][1]

    total = (
        sum(s for _, s in tiny)
        + sum(s for _, s in cache_dirs)
        + sum(s for _, s in logs)
        + duplicate_reclaimable
    )
    return {
        "tiny": tiny,
        "cache_dirs": cache_dirs,
        "logs": logs,
        "duplicates": duplicates,
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
    """Print summary with sentences 'Hay X ... y en conjunto pesan Y MB' and table."""
    n_tiny = len(summary["tiny"])
    s_tiny = sum(s for _, s in summary["tiny"])
    n_cache = len(summary["cache_dirs"])
    s_cache = sum(s for _, s in summary["cache_dirs"])
    n_logs = len(summary["logs"])
    s_logs = sum(s for _, s in summary["logs"])
    dup = summary.get("duplicates") or []
    n_dup = len(dup)
    s_dup = sum(s for _, s in dup)
    # Reclaimable from duplicates is (N-1)*size per group; we show total size of listed dup files
    console.print("[bold cyan]Cleanup summary[/bold cyan]")
    console.print(f"  Hay [yellow]{n_cache}[/yellow] archivos de caché y en conjunto pesan [cyan]{_size_mb(s_cache)}[/cyan].")
    console.print(f"  Hay [yellow]{n_logs}[/yellow] archivos de logs y en conjunto pesan [cyan]{_size_mb(s_logs)}[/cyan].")
    console.print(f"  Hay [yellow]{n_tiny}[/yellow] archivos muy pequeños y en conjunto pesan [cyan]{_size_mb(s_tiny)}[/cyan].")
    console.print(f"  Hay [yellow]{n_dup}[/yellow] archivos duplicados (excl. programación) y en conjunto pesan [cyan]{_size_mb(s_dup)}[/cyan].")
    table = Table(
        title="Detalle por categoría",
        title_style="bold cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Category", style="green")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Size", justify="right", style="cyan")
    table.add_row("Cache dirs / files", str(n_cache), _size_mb(s_cache))
    table.add_row("Log files", str(n_logs), _size_mb(s_logs))
    table.add_row("Tiny files (< 1 KB)", str(n_tiny), _size_mb(s_tiny))
    table.add_row("Duplicates (excl. code)", str(n_dup), _size_mb(s_dup))
    table.add_row("", "", "")
    table.add_row("[bold]Total reclaimable[/bold]", str(n_tiny + n_cache + n_logs + n_dup), _size_mb(summary["total_reclaimable"]))
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
        elif p.is_dir() and p.name.lower() in {d.lower() for d in CACHE_DIR_NAMES}:
            try:
                shutil.rmtree(p)
            except OSError as e:
                console.print(f"[red]Failed to remove dir {p}: {e}[/red]")
                ok = False
    for path_str, _ in summary.get("duplicates") or []:
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
