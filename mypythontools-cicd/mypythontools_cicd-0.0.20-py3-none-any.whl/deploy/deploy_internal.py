"""Module with functions for 'deploy' subpackage."""

from __future__ import annotations
import os
import shutil

import mylogging

from mypythontools.paths import validate_path, PathLike
from mypythontools.misc import delete_files
from mypythontools.system import check_script_is_available, terminal_do_command, PYTHON

from mypythontools_cicd.project_paths import PROJECT_PATHS


def deploy_to_pypi(
    setup_path: None | PathLike = None, clean: bool = True, verbose: bool = True, pep517: bool = True
) -> None:
    """Publish python library to PyPi.

    Username and password are set with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-starter on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path (None | PathLike, optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, path will be inferred. Build and dist folders will be created in same directory.
            Defaults to None.
        clean (bool, optional): Whether delete created build and dist folders.
        verbose (bool, optional): If True, result of terminal command will be printed to console.
            Defaults to False.
        pep517 (bool, optional): Whether using PEP 517, that use pyproject.toml to build distribution.
    """
    usr = os.environ.get("TWINE_USERNAME")
    password = os.environ.get("TWINE_PASSWORD")

    if not usr or not password:
        raise KeyError("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")

    check_script_is_available("twine", "twine")

    setup_path = PROJECT_PATHS.root / "setup.py" if not setup_path else validate_path(setup_path)

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    delete_files(dist_path)
    delete_files(build_path)

    if pep517:
        build_command = f"{PYTHON} -m build --wheel --sdist"
    else:
        build_command = f"{PYTHON} setup.py sdist bdist_wheel"

    terminal_do_command(
        build_command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header="Build python distribution for PyPi deployment failed. Try to set 'pep517' to False.",
    )

    command = f"twine upload dist/*"

    terminal_do_command(
        command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header="Deploying to PyPi failed.",
    )

    if clean:
        delete_files(dist_path)
        delete_files(build_path)
