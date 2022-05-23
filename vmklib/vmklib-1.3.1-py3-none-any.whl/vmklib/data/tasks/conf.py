"""
A module for registering package tasks.
"""

# built-in
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.task.dict.melder import DictMerger
from vcorelib.task.manager import TaskManager

# internal
from vmklib.tasks.python import venv_bin, venv_dir
from vmklib.tasks.venv import register as register_venv


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register package tasks to the manager."""

    # Set up initial data so that every task has easy access to common
    # definitions.
    init_data = {
        "__dirs__": {
            "build": cwd.joinpath("build"),
            "venv": venv_dir(cwd),
            "venv_bin": venv_bin(cwd),
            "proj": cwd.joinpath(project),
        },
        "__files__": {"python": venv_bin(cwd, "python")},
    }

    # Register the initialization task.
    manager.register(DictMerger("vmklib.init", init_data, substitutions))

    # Load additional modules.
    result = True
    for dep in [register_venv]:
        if result:
            result = dep(manager, project, cwd, substitutions)

    return result
