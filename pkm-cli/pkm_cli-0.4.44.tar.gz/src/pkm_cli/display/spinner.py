from contextlib import contextmanager
from typing import ContextManager, Optional

from rich.console import ConsoleRenderable
from rich.spinner import Spinner as RichSpinner
from time import time

from pkm_cli.display.display import InformationUnit, Display


class Spinner(InformationUnit):

    def __init__(self, description: str):
        self._description = description
        self._rich_spinner: Optional[RichSpinner] = None

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value
        if r := self._rich_spinner:
            r.update(text=value)

    @contextmanager
    def dumb(self) -> ContextManager:
        starttime = time()
        Display.print(f"[START] {self._description}")
        yield
        Display.print(f"[END] {self._description}, took: {time() - starttime} seconds")

    @contextmanager
    def rich(self) -> ContextManager[ConsoleRenderable]:
        starttime = time()

        self._rich_spinner = RichSpinner("dots", self._description, style="progress.spinner")
        yield self._rich_spinner

        if Display.verbose:
            Display.print(f"Done {self._description}, took: {time() - starttime:.2f} seconds")
