"""
Estado de carga para operaciones CLI.

Carga estandar: barra de progreso (izquierda a derecha) basada en tiempo, ya que los
workers no reportan progreso real (KISS). Operaciones largas: barra hasta 90 %% en 20 s,
luego 100 %% al terminar; opcional mensaje typewriter al final.
Operaciones cortas: solo "Working on it...".
Durante el worker se redirige stderr para no mostrar mensajes de librerias (p. ej. pypdf).
"""

import io
import sys
import time
import threading
from contextlib import redirect_stderr
from typing import Any, Callable, TypeVar

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

_console = Console()

# Barra: tiempo max para llegar a 90 %% (workers no exponen progreso)
PROGRESS_BAR_MAX_SECONDS = 20
PROGRESS_BAR_TARGET = 90
PROGRESS_UPDATE_INTERVAL = 0.35

LOADING_PHRASES_LONG = [
    "Trying different spells...",
    "Charging mana pool...",
    "Summoning undead file searcher...",
    "Contacting the File Monster...",
    "Contacting my grandma, maybe she can help...",
    "This is harder than I thought...",
]
LOADING_PHRASE_SHORT = "Working on it..."
DONE_MESSAGE = "The File Master has AWAKEN!!!!"
TYPEWRITER_DELAY = 0.05
PHRASE_INTERVAL = 3.0
DONE_PAUSE = 0.5
LOADING_LONG_THRESHOLD_SECONDS = 5
SPINNER_CHARS = ["|", "/", "-", "\\"]
SPINNER_INTERVAL = 0.15
# Estilo ANSI para frases largas: bold + magenta (morado)
_STYLE_BOLD_MAGENTA = "\033[1m\033[35m"
_STYLE_RESET = "\033[0m"

IMPORT_PHRASES = [
    "Importing files...",
    "This spell is a bit slow, I'll try another one...",
    "Aha! I got it, just a little more of git extract...",
    "This is taking longer than expected...",
    "Almost there...",
]
IMPORT_PHRASE_INTERVAL = 3.0
IMPORT_DONE_MESSAGE = "Done!"
SCAN_DONE_MESSAGE = "all done <):D"
SCAN_DONE_PAUSE_SECONDS = 1.0

T = TypeVar("T")


def _terminal_columns() -> int:
    """Columnas del terminal; 80 si no disponible."""
    try:
        import shutil
        return shutil.get_terminal_size().columns or 80
    except Exception:
        return 80


def _center_text(text: str, width: int | None = None) -> str:
    """Centra el texto en el ancho dado (o terminal)."""
    w = width if width is not None else _terminal_columns()
    return text.center(w)


def _print_centered(text: str, style: str = "cyan") -> None:
    """Imprime texto centrado con estilo Rich."""
    centered = _center_text(text)
    _console.print(centered, style=style)


def _typewriter_print(text: str, style: str = "bold yellow", delay: float = TYPEWRITER_DELAY) -> None:
    """Imprime texto letra a letra (animacion typewriter)."""
    for char in text:
        _console.print(char, end="", style=style)
        sys.stdout.flush()
        time.sleep(delay)
    _console.print()
    time.sleep(DONE_PAUSE)


def run_with_loading_short(
    worker: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Ejecuta worker mostrando 'Working on it...' (centrado) y devuelve el resultado. stderr suprimido durante el worker."""
    _print_centered(LOADING_PHRASE_SHORT, style="cyan")
    with redirect_stderr(io.StringIO()):
        return worker(*args, **kwargs)


def run_with_loading_long(
    worker: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Ejecuta worker en un thread; muestra barra de progreso (time-based) y al terminar DONE_MESSAGE."""
    result_container: list[Any] = []
    exc_container: list[BaseException] = []

    def run_worker() -> None:
        try:
            with redirect_stderr(io.StringIO()):
                result_container.append(worker(*args, **kwargs))
        except BaseException as e:
            exc_container.append(e)

    thread_done = threading.Event()
    start_time = time.monotonic()

    def run_and_signal() -> None:
        run_worker()
        thread_done.set()

    t = threading.Thread(target=run_and_signal)
    t.start()

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=_console,
    )
    with progress:
        task = progress.add_task("Loading...", total=100)
        while not thread_done.is_set():
            elapsed = time.monotonic() - start_time
            completed = min(PROGRESS_BAR_TARGET, int((elapsed / PROGRESS_BAR_MAX_SECONDS) * PROGRESS_BAR_TARGET))
            progress.update(task, completed=completed)
            thread_done.wait(timeout=PROGRESS_UPDATE_INTERVAL)
        progress.update(task, completed=100)

    t.join()

    if exc_container:
        _console.print("[red]Error during operation.[/red]")
        raise exc_container[0]

    if not result_container:
        raise RuntimeError("Worker did not set result")

    _typewriter_print(DONE_MESSAGE)
    return result_container[0]


def run_with_loading_scan(
    worker: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Same progress bar as run_with_loading_long, but at the end shows 'all done <):D' for 1 second (no typewriter)."""
    result_container: list[Any] = []
    exc_container: list[BaseException] = []

    def run_worker() -> None:
        try:
            with redirect_stderr(io.StringIO()):
                result_container.append(worker(*args, **kwargs))
        except BaseException as e:
            exc_container.append(e)

    thread_done = threading.Event()
    start_time = time.monotonic()

    def run_and_signal() -> None:
        run_worker()
        thread_done.set()

    t = threading.Thread(target=run_and_signal)
    t.start()

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=_console,
    )
    with progress:
        task = progress.add_task("Loading...", total=100)
        while not thread_done.is_set():
            elapsed = time.monotonic() - start_time
            completed = min(PROGRESS_BAR_TARGET, int((elapsed / PROGRESS_BAR_MAX_SECONDS) * PROGRESS_BAR_TARGET))
            progress.update(task, completed=completed)
            thread_done.wait(timeout=PROGRESS_UPDATE_INTERVAL)
        progress.update(task, completed=100)

    t.join()

    if exc_container:
        _console.print("[red]Error during operation.[/red]")
        raise exc_container[0]

    if not result_container:
        raise RuntimeError("Worker did not set result")

    _console.print(_center_text(SCAN_DONE_MESSAGE), style="bold green")
    time.sleep(SCAN_DONE_PAUSE_SECONDS)
    return result_container[0]


def run_with_import_loading(
    worker: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Ejecuta worker en un thread; muestra barra de progreso (time-based) y al terminar 'Done!'."""
    result_container: list[Any] = []
    exc_container: list[BaseException] = []

    def run_worker() -> None:
        try:
            with redirect_stderr(io.StringIO()):
                result_container.append(worker(*args, **kwargs))
        except BaseException as e:
            exc_container.append(e)

    thread_done = threading.Event()
    start_time = time.monotonic()

    def run_and_signal() -> None:
        run_worker()
        thread_done.set()

    t = threading.Thread(target=run_and_signal)
    t.start()

    progress = Progress(
        TextColumn("[bold green]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=_console,
    )
    with progress:
        task = progress.add_task("Importing...", total=100)
        while not thread_done.is_set():
            elapsed = time.monotonic() - start_time
            completed = min(PROGRESS_BAR_TARGET, int((elapsed / 15) * PROGRESS_BAR_TARGET))
            progress.update(task, completed=completed)
            thread_done.wait(timeout=PROGRESS_UPDATE_INTERVAL)
        progress.update(task, completed=100)

    t.join()

    if exc_container:
        _console.print("[red]Error during operation.[/red]")
        raise exc_container[0]

    if not result_container:
        raise RuntimeError("Worker did not set result")

    _console.print(_center_text(IMPORT_DONE_MESSAGE), style="bold green")
    return result_container[0]
