"""
vmklib - This package's command-line entry-point application.
"""

# built-in
import argparse
from asyncio import get_event_loop
from contextlib import contextmanager
from json import load
import logging
import os
from pathlib import Path
from platform import system
import subprocess
import tempfile
from typing import Callable, Dict, Iterator

# third-party
import pkg_resources
from vcorelib.paths import find_file
from vcorelib.task.manager import TaskManager

# internal
from vmklib import PKG_NAME

LOG = logging.getLogger(__name__)
DEFAULT_FILE = Path("Makefile")


def get_resource(resource_name: str) -> Path:
    """Locate the path to a package resource."""

    resource_path = str(Path(os.path.join("data", resource_name)).parent)

    locations = [
        pkg_resources.resource_filename(__name__, resource_path),
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            resource_path,
        ),
    ]
    found = find_file(
        Path(resource_name).name,
        locations,
    )

    # ensure that the resource can actually be found
    assert found is not None, (
        f"Couldn't load resource '{resource_name}' in: "
        f"{', '.join(locations)}!"
    )
    return found


def project(path: Path, name: str = None) -> str:
    """
    If the project name wasn't provided, guess that it's either the name
    of the parent directory, or that name as a slug.
    """
    path = path.resolve()
    if name is None:
        parent_slug = path.name.replace("-", "_")
        if path.joinpath(parent_slug).is_dir():
            name = parent_slug
        else:
            name = str(path.name)

    return name


@contextmanager
def build_makefile(
    user_file: Path,
    directory: Path,
    proj: str,
    data: dict,
) -> Iterator[str]:
    """Build a temporary makefile and return the path."""

    # create a temporary file
    with tempfile.NamedTemporaryFile(mode="w") as makefile:
        # build the necessary file data
        data["PROJ"] = proj
        data["$(PROJ)_DIR"] = directory
        data["MK_AUTO"] = 1
        data["$(PROJ)_MK_DIR"] = os.path.join(data["$(PROJ)_DIR"], "mk")

        # get the path to this package's data to include our "conf.mk"
        include_strs = [
            "-include $($(PROJ)_MK_DIR)/init.mk",
            f"include {get_resource('conf.mk')}",
            "-include $($(PROJ)_MK_DIR)/conf.mk",
        ]

        for key, item in data.items():
            makefile.write(f"{key} := {item}")
            makefile.write(os.linesep)
        for line in include_strs:
            makefile.write(line)
            makefile.write(os.linesep)

        makefile.write(os.linesep)

        # read the user's file
        with user_file.open(encoding="utf-8") as user_makefile:
            makefile.write(user_makefile.read())

        makefile.flush()
        yield makefile.name


#
# A function from an external module that's given:
#
# - project name
# - working directory (not necessarily the current one)
# - task manager to register tasks to
#
TaskRegister = Callable[[TaskManager, str, Path, Dict[str, str]], bool]


def initialize_task_manager(
    manager: TaskManager,
    proj: str,
    task_register: str,
    directory: Path,
    substitutions: Dict[str, str],
) -> None:
    """Load internal and external tasks to the task manager."""

    # register task-manager targets from this package
    assert manager.script(
        get_resource(task_register),
        "register",
        proj,
        directory,
        substitutions,
    ), "Couldn't register package tasks from '{get_resource(task_register)}'!"

    # register task-manager targets for the project
    proj_tasks = None
    try:
        proj_tasks = get_resource(os.path.join(directory, task_register))
    except AssertionError:
        pass
    if proj_tasks is not None and proj_tasks.is_file():
        assert manager.script(
            proj_tasks,
            "register",
            proj,
            directory,
            substitutions,
        ), "Couldn't register project tasks from '{proj_tasks}'!"


def get_data(path: Path) -> dict:
    """Load configuration data if it can be found."""

    # load configuration data, if configuration data is found
    data = {}
    if path.is_file():
        with path.open(encoding="utf-8") as config_fd:
            data = load(config_fd)
            assert isinstance(
                data, dict
            ), f"Configuration from '{path}', is not an object!"

    return data


def entry(args: argparse.Namespace) -> int:
    """Execute the requested task."""

    if not args.file.is_file():
        if args.file.name != str(DEFAULT_FILE):
            LOG.error("'%s' not found", args.file)
            return 1
        args.file = get_resource(os.path.join("data", "header.mk"))

    # load configuration data, if configuration data is found
    substitutions: Dict[str, str] = get_data(args.config)

    proj = project(args.dir, args.proj)
    task_register = os.path.join("tasks", "conf.py")

    manager = TaskManager()
    initialize_task_manager(
        manager, proj, task_register, args.dir, substitutions
    )

    # build the list of targets to execute
    target_args = []
    for target in args.targets:
        target_str = target
        if args.prefix and "=" not in target_str:
            target_str = f"{args.prefix}-{target_str}"
        target_args.append(target_str)

    # determine which tasks aren't resolved by the task manager
    unresolved, executor = manager.prepare_execute(
        target_args, **substitutions
    )

    # execute tasks handled by the task manager
    get_event_loop().run_until_complete(executor())

    retcode = 1

    # Handle Make targets if it makes sense to run make.
    if unresolved and not args.disable_make and not system() == "Windows":
        invocation_args = ["make", "-C", str(args.dir), "-f"]
        with build_makefile(
            args.file, args.dir, proj, substitutions
        ) as makefile:
            invocation_args.append(makefile)
            invocation_args += list(unresolved)
            LOG.debug(invocation_args)
            try:
                result = subprocess.run(invocation_args, check=True)
                retcode = result.returncode
            except subprocess.CalledProcessError as exc:
                retcode = exc.returncode
            except KeyboardInterrupt:
                pass

    # Set the return code to zero if all targets were resolved.
    elif not unresolved:
        retcode = 0
    else:
        print(
            f"The following targets were not resovled: {', '.join(unresolved)}"
        )

    return retcode


def add_app_args(parser: argparse.ArgumentParser) -> None:
    """Add application-specific arguments to the command-line parser."""

    parser.add_argument("targets", nargs="*", help="targets to execute")
    parser.add_argument(
        "-p", "--prefix", default="", help="a prefix to apply to all targets"
    )
    parser.add_argument(
        "-d",
        "--disable-make",
        action="store_true",
        help="whether or not to allow GNU Make target resolution",
    )
    parser.add_argument(
        "-f",
        "--file",
        default=DEFAULT_FILE,
        type=Path,
        help=(
            "file to source user-provided recipes from "
            "(default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_FILE.parent.joinpath(f"{PKG_NAME}.json"),
        type=Path,
        help=(
            "file to source user-provided variable definitions, ahead of "
            "loading package makefiles (default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-P", "--proj", type=str, help="project name for internal variable use"
    )
