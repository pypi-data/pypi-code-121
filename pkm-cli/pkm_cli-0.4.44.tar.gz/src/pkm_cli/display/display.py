import atexit
import os
from abc import abstractmethod
from contextlib import contextmanager
from rich.theme import Theme
from threading import RLock, Thread, Condition
from typing import Optional, Protocol, TypeVar, ContextManager, List

from rich.console import ConsoleRenderable, Console, ConsoleOptions, RenderResult
from rich.live import Live
from time import sleep
import questionary as q

_PKM_THEME = Theme({
    'h1': "green_yellow"
})


class InformationUnit(Protocol):
    @abstractmethod
    def dumb(self) -> ContextManager:
        ...

    @abstractmethod
    def rich(self) -> ContextManager[ConsoleRenderable]:
        ...


_T = TypeVar("_T", bound=InformationUnit)

console_lock = RLock()


class _LiveOutput(ConsoleRenderable):
    def __init__(self, console: Console):
        self._live_renderer: Optional[Live] = Live(
            self, console=console, auto_refresh=False, redirect_stdout=False,
            redirect_stderr=False)
        self._live_components: List[ConsoleRenderable] = []
        self._live_renderer.__enter__()
        self._requires_render = Condition()

        Thread(name="live output refresher", target=self._refresh_loop, daemon=True).start()
        atexit.register(lambda: print("\x1b[?25h"))  # make sure the cursor is re-shown after python exiting

    def _refresh_loop(self):
        empty_rendered = False
        while True:
            if self._live_components or not empty_rendered:

                with console_lock:
                    self._live_renderer.refresh()

                empty_rendered = not self._live_components
                sleep(0.2)
            else:
                with self._requires_render:
                    if not self._live_components:
                        self._requires_render.wait()

    def __rich_console__(self, console: "Console", options: "ConsoleOptions") -> "RenderResult":
        return self._live_components

    @contextmanager
    def show(self, iu: InformationUnit):
        with iu.rich() as renderable:
            with self._requires_render:
                self._live_components = [renderable, *self._live_components]
                if len(self._live_components) == 1:
                    self._requires_render.notify_all()

            try:
                yield
            finally:
                self._live_components = [c for c in self._live_components if c is not renderable]


# noinspection PyMethodMayBeStatic
class _Display:

    def __init__(self, dumb: Optional[bool] = None):
        self._console = Console(theme=_PKM_THEME)
        self._dumb = self._console.is_dumb_terminal if dumb is None else dumb
        self._live_output = None if self._dumb else _LiveOutput(self._console)
        self.verbose = False

        if self._dumb:
            self.print("using dumb display")

    def print(self, msg: str, *, newline: bool = True, use_markup: bool = True):
        with console_lock:
            self._console.print(msg, end=os.linesep if newline else '', markup=use_markup)

    def ask(self, prompt: str) -> str:
        return q.text(prompt).ask()

    def ask_password(self, prompt: str) -> str:
        return q.password(prompt).ask()

    @contextmanager
    def show(self, iu: _T) -> _T:
        if self._dumb:
            with iu.dumb():
                yield iu
        else:
            with self._live_output.show(iu):
                yield iu

    def is_dumb(self) -> bool:
        return self._dumb


Display = _Display()
