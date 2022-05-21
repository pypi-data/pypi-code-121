from contextlib import contextmanager

from rich.console import ConsoleRenderable
from rich.progress import Progress as RichProgress
from time import time
from typing import Any, ContextManager, Optional

from pkm_cli.display.display import InformationUnit, console_lock, Display


class Progress(InformationUnit):

    def __init__(self, description: str, total: int = 100):
        self._description = description
        self._total = total
        self._completed = 0
        self._rich_progress: Optional[RichProgress] = None
        self._rich_progress_task: Any = None

    @contextmanager
    def dumb(self) -> ContextManager:
        starttime = time()
        Display.print(f"[START] {self._description}")
        yield
        Display.print(f"[END] {self._description}, took: {time() - starttime:.2f} seconds")

    @contextmanager
    def rich(self) -> ContextManager[ConsoleRenderable]:
        starttime = time()
        self._rich_progress = RichProgress()
        self._rich_progress_task = self._rich_progress.add_task(
            self._description, total=self._total, completed=self._completed)

        yield self._rich_progress

        if Display.verbose:
            Display.print(f"Done {self._description}, took: {time() - starttime:.2f} seconds")

    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, v: int):
        self._total = v
        if self._rich_progress:
            with console_lock:
                self._rich_progress.update(self._rich_progress_task, total=v, refresh=False)

    @property
    def completed(self) -> int:
        return self._completed

    @completed.setter
    def completed(self, v: int):
        self._completed = v
        if self._rich_progress:
            with console_lock:
                self._rich_progress.update(self._rich_progress_task, completed=v, refresh=False)
