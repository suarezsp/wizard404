"""
Estado de carga para operaciones CLI.

Carga estandar: spinner rotativo. Si la operacion supera LOADING_LONG_THRESHOLD_SECONDS,
se muestran frases rotativas y al terminar "The File Master has AWAKEN!!!!" con typewriter.
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

_console = Console()

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
    """Ejecuta worker en un thread. Hasta 5 s: spinner; si tarda más: frases rotativas y DONE_MESSAGE typewriter."""
    result_container: list[Any] = []
    exc_container: list[BaseException] = []

    def run_worker() -> None:
        try:
            with redirect_stderr(io.StringIO()):
                result_container.append(worker(*args, **kwargs))
        except BaseException as e:
            exc_container.append(e)

    columns = _terminal_columns()
    thread_done = threading.Event()
    start_time = time.monotonic()
    used_long_phrases = False

    def run_and_signal() -> None:
        run_worker()
        thread_done.set()

    t = threading.Thread(target=run_and_signal)
    t.start()

    spinner_index = 0
    phrase_index = 0
    try:
        while not thread_done.is_set():
            elapsed = time.monotonic() - start_time
            if elapsed < LOADING_LONG_THRESHOLD_SECONDS:
                # Spinner solo
                sym = SPINNER_CHARS[spinner_index % len(SPINNER_CHARS)]
                centered = _center_text(f"  {sym}  ")
                sys.stdout.write("\r" + centered + " " * max(0, columns - len(centered)) + "\r")
                sys.stdout.flush()
                spinner_index += 1
                thread_done.wait(timeout=SPINNER_INTERVAL)
            else:
                # Frases rotativas (bold magenta)
                used_long_phrases = True
                phrase = LOADING_PHRASES_LONG[phrase_index % len(LOADING_PHRASES_LONG)]
                centered = _center_text(phrase)
                sys.stdout.write(
                    "\r" + _STYLE_BOLD_MAGENTA + centered + _STYLE_RESET
                    + " " * max(0, columns - len(centered)) + "\r"
                )
                sys.stdout.flush()
                phrase_index += 1
                thread_done.wait(timeout=PHRASE_INTERVAL)
    except Exception:
        pass
    t.join()

    # Limpiar línea de carga
    sys.stdout.write("\r" + " " * columns + "\r")
    sys.stdout.flush()

    if exc_container:
        _console.print("[red]Error during operation.[/red]")
        raise exc_container[0]

    if not result_container:
        raise RuntimeError("Worker did not set result")

    if used_long_phrases:
        _typewriter_print(DONE_MESSAGE)
    return result_container[0]


def run_with_import_loading(
    worker: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Ejecuta worker en un thread; muestra frases de import cada 3 s (bold magenta), luego 'Listo!'. stderr suprimido."""
    result_container: list[Any] = []
    exc_container: list[BaseException] = []

    def run_worker() -> None:
        try:
            with redirect_stderr(io.StringIO()):
                result_container.append(worker(*args, **kwargs))
        except BaseException as e:
            exc_container.append(e)

    columns = _terminal_columns()
    thread_done = threading.Event()

    def run_and_signal() -> None:
        run_worker()
        thread_done.set()

    t = threading.Thread(target=run_and_signal)
    t.start()

    phrase_index = 0
    try:
        while not thread_done.is_set():
            phrase = IMPORT_PHRASES[phrase_index % len(IMPORT_PHRASES)]
            centered = _center_text(phrase)
            sys.stdout.write(
                "\r" + _STYLE_BOLD_MAGENTA + centered + _STYLE_RESET
                + " " * max(0, columns - len(centered)) + "\r"
            )
            sys.stdout.flush()
            phrase_index += 1
            thread_done.wait(timeout=IMPORT_PHRASE_INTERVAL)
    except Exception:
        pass
    t.join()

    sys.stdout.write("\r" + " " * columns + "\r")
    sys.stdout.flush()

    if exc_container:
        _console.print("[red]Error during operation.[/red]")
        raise exc_container[0]

    if not result_container:
        raise RuntimeError("Worker did not set result")

    _console.print(_center_text(IMPORT_DONE_MESSAGE), style="bold green")
    return result_container[0]
