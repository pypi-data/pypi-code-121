"""
A module for registering virtual environment tasks.
"""

# built-in
from os.path import join
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.dict import set_if_not
from vcorelib.paths import get_file_name
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

# internal
from vmklib.resources import get_resource
from vmklib.tasks.mixins.concrete import ConcreteBuilderMixin
from vmklib.tasks.python import python_version as _python_version
from vmklib.tasks.python import venv_bin, venv_dir


class Venv(ConcreteBuilderMixin, SubprocessLogMixin):
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
        python = venv_bin(cwd, "python", python_version)
        if path.is_dir() and python.is_file():
            self._continue = False
            self.update_concrete(_inbox, **_kwargs)

        # Set the path in the outbox so we can easily find it.
        _outbox["path"] = path
        _outbox["python"] = python
        return True

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Create or update a project's virtual environment."""

        result = True

        # Run the command.
        version = kwargs.get("python_version", _python_version())
        proc = await self.subprocess_exec(
            f"python{version}", "-m", "venv", str(outbox["path"])
        )
        await proc.communicate()
        result = proc.returncode == 0

        # Upgrade pip by default.
        if result and kwargs.get("upgrade_pip", True):
            proc = await self.subprocess_exec(
                str(outbox["python"]),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            )
            await proc.communicate()
            result = proc.returncode == 0

        return result


class RequirementsInstaller(ConcreteBuilderMixin, SubprocessLogMixin):
    """A task for installing requirements files."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Install a requirements file."""

        result = True

        # Only take action if any of the requirements are newer than the
        # concrete.
        req_files = [*args]
        self._continue = self.is_concrete_stale(inbox, req_files, {**kwargs})
        if self._continue:
            for req in req_files:
                if result:
                    # Run the command.
                    proc = await self.subprocess_exec(
                        str(inbox["venv{python_version}"]["python"]),
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(req),
                    )
                    await proc.communicate()
                    result = proc.returncode == 0

        return result


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
    manager.register(Phony("venv"), ["venv{python_version}"])

    requirements_files = [
        # Project requirements.
        cwd.joinpath(project, "requirements.txt"),
        cwd.joinpath(project, "dev_requirements.txt"),
        # Package's default requirements.
        get_resource(join("data", "edit_venv.txt")),
        get_resource(join("data", "fresh_venv.txt")),
    ]

    # Ensure we can load the package requirements files.
    assert requirements_files[2].is_file()
    assert requirements_files[3].is_file()

    # Register requirements' install tasks.
    for req in requirements_files:
        if req.is_file():
            task_name = f"python-requirements-{get_file_name(req)}"
            manager.register(
                RequirementsInstaller(task_name, req),
                ["vmklib.init", "venv{python_version}"],
            )
            manager.register_to("venv", [task_name])

    return True
