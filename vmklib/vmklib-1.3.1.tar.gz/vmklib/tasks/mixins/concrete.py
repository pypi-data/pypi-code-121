"""
A task mixin for writing concrete outputs to a build directory.
"""

# built-in
from os import linesep
from pathlib import Path
from time import asctime
from typing import Dict, Iterable

# third-party
from vcorelib.paths import Pathlike, modified_after
from vcorelib.task import Inbox, Outbox, Task


class ConcreteBuilderMixin(Task):
    """Create a concrete file output after a task completes."""

    def concrete_path(
        self,
        inbox: Inbox,
        substitutions: Dict[str, str] = None,
    ) -> Path:
        """By default name the concrete after the compiled target name."""

        init_data = inbox["vmklib.init"]
        build = init_data["__dirs__"]["build"]
        return build.joinpath(f"{self.target.compile(substitutions)}.txt")

    def is_concrete_stale(
        self,
        inbox: Inbox,
        candidates: Iterable[Pathlike],
        substitutions: Dict[str, str] = None,
    ) -> bool:
        """Check if any candidate paths are modified after the concrete was."""

        return modified_after(
            self.concrete_path(inbox, substitutions), candidates
        )

    def update_concrete(self, inbox: Inbox, **kwargs) -> Path:
        """
        Write a text file to disk in the build directory based on the name of
        this task.

        This is useful to bootstrap compatibility with other tools like GNU
        Make that assess concrete targets.
        """

        concrete = self.concrete_path(inbox, {**kwargs})

        # Write data to the concrete file.
        concrete.parent.mkdir(parents=True, exist_ok=True)
        with concrete.open("w", encoding="utf-8") as concrete_fd:
            concrete_fd.write(asctime())
            concrete_fd.write(linesep)
        return concrete

    async def run_exit(
        self, _inbox: Inbox, _outbox: Outbox, *_args, **kwargs
    ) -> bool:
        """Update the concrete target after main execution by default."""

        _outbox["concrete"] = self.update_concrete(_inbox, **kwargs)
        return True
