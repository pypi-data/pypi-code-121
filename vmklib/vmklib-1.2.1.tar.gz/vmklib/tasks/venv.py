"""
A module for registering virtual environment tasks.
"""

# built-in
from asyncio import create_subprocess_exec
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.dict import set_if_not
from vcorelib.task import Inbox, Outbox, Task
from vcorelib.task.manager import TaskManager

# internal
from vmklib.tasks.mixins.concrete import ConcreteBuilderMixin
from vmklib.tasks.python import python_version as _python_version
from vmklib.tasks.python import venv_bin, venv_dir


class Venv(ConcreteBuilderMixin):
    """A target prototype for creating a virtual environment."""

    async def run_enter(
        self,
        _inbox: Inbox,
        _outbox: Outbox,
        *_args,
        **_kwargs,
    ) -> bool:
        """A default enter method."""

        cwd: Path = _args[0]
        python_version = _kwargs.get("python_version", _python_version())
        path = venv_dir(cwd, python_version)

        # If the environment already exists we don't need to create it.
        if path.is_dir() and venv_bin(cwd, "python", python_version).is_file():
            self._continue = False
            self.update_concrete(_inbox, **_kwargs)

        # Set the path in the outbox so we can easily find it.
        _outbox["path"] = path
        return True

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Create or update a project's virtual environment."""

        # Run the command.
        version = kwargs.get("python_version", _python_version())
        proc = await create_subprocess_exec(
            f"python{version}", "-m", "venv", str(outbox["path"])
        )
        await proc.communicate()
        return proc.returncode == 0


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register virtual environment tasks to the manager."""

    # Ensure that a valid version is set.
    set_if_not(substitutions, "python_version", _python_version())

    # The target that actually creates the initial environment.
    manager.register(Venv("venv{python_version}", cwd), ["vmklib.init"])

    # Add a "phony" style target to just create the virtual environment. Here
    # We would also add dependencies like requirement-file installs.
    manager.register(Task("venv"), ["venv{python_version}"])

    del project
    return True
