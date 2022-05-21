"""Module with functions for 'build' subpackage."""
from __future__ import annotations
from typing import Sequence
import shutil
from pathlib import Path
import sys

from typing_extensions import Literal
from mypythontools.paths import PathLike, find_path, validate_path
from mypythontools.misc import delete_files
from mypythontools.system import (
    check_script_is_available,
    check_library_is_available,
    get_console_str_with_quotes,
    terminal_do_command,
)

import mylogging

from ..project_paths import PROJECT_PATHS
from .. import venvs

# Lazy imports
# import EelForkExcludeFiles


def build_app(
    root_path: None | str | Path = None,
    main_file: str | Path = "app.py",
    preset: Literal["eel", None] = None,
    web_path: None | str | Path = None,
    build_web: bool | str = "preset",
    virtualenv: None | PathLike = sys.prefix,
    sync_requirements: None | Literal["infer"] | PathLike | Sequence[PathLike] = "infer",
    remove_last_build: bool = False,
    console: bool = True,
    debug: bool = False,
    icon: str | Path | None = None,
    hidden_imports: None | list[str] = None,
    ignored_packages: None | list[str] = None,
    datas: None | list[tuple[str, str]] = None,
    env_vars: None | dict = None,
    name: None | str = None,
    clean: bool = True,
    verbosity: Literal[0, 1, 2] = 1,
) -> None:
    """One script to build .exe app from source code on windows.

    This script automatically generate .spec file, build node web files and add environment variables during
    build.

    This script suppose some structure of the app (may have way different though). You can use project-starter
    from the same repository, if you start with application.

    Args:
        root_path (None | str | Path, optional): Path of root folder where build and dist folders will be
            placed. If None, path is inferred. Defaults to None.
        main_file (str, optional): Main file path or name with extension. Main file is found automatically
            and don't have to be in root. Defaults to 'app.py'.
        preset (Literal['eel', None], optional): Edit other params for specific use cases (append to
            hidden_imports, datas etc.). Defaults to None.
        web_path (None | str | Path, optional): If using eel preset it's folder with index.html. If None,
            path is inferred. Defaults to None.
        build_web (bool | str, optional): If application contain package.json build node application.
            If 'preset' build automatically depending on preset. Defaults to 'preset'.
        virtualenv (None | PathLike, optional): Whether run in virtualenv. If you want to use current venv,
            use ``sys.prefix``. Defaults to sys.prefix.
        sync_requirements (None | Literal["infer"] | PathLike | Sequence[PathLike], optional): If using
            `virtualenv` define what libraries will be installed by path to requirements.txt. Can also be a
            list of more files e.g `["requirements.txt", "requirements_dev.txt"]`. If "infer", autodetected
            (all requirements). Defaults to "infer".
        remove_last_build (bool, optional): If some problems, it is possible to delete build and dist folders.
            Defaults to False.
        console (bool, optional): Before app run terminal window appears (good for debugging).
            Defaults to False.
        debug (bool, optional): If no console, then dialog window with traceback appears.
            Defaults to False.
        icon (None | str | Path, optional): Path or name with extension to .ico file (!no png!).
            Defaults to None.
        hidden_imports (None | list, optional): If app is not working, it can be because some library was
            not builded. Add such libraries into this list. Defaults to None.
        ignored_packages (None | list, optional): Libraries take space even if not necessary.
            Defaults to None.
        datas (None | list[tuple[str, str], optional): Add static files to build.
            Example: [('my_source_path, 'destination_path')]. Defaults to None.
        env_vars (None | dict, optional): Add some env vars during build. Mostly to tell main script that
            it's production (ne development) mode. Defaults to None.
        name (None | str, optional): If name of app is different than main py file. Defaults to None.
        clean (bool, optional): Remove spec file and var env py hook. Defaults to True.
        verbosity (Literal[0, 1, 2], optional): How much information print to console. 0 prints just errors,
            1 prints when starting new step, 2 prints every stdout to console. Defaults to 1.

    Note:
        Build pyinstaller bootloader on your pc, otherwise antivirus can check the
        file for a while on first run and even alert false positive.

        Download from github, cd to bootloader and::

            python ./waf all

        Back to pyinstaller folder and python `setup.py`
    """
    # if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    #     raise RuntimeError(mylogging.format_str("Python version >=3.10 not supported yet."))

    check_script_is_available("pyinstaller")

    verbose = True if verbosity == 2 else False

    if not hidden_imports:
        hidden_imports = []

    if not ignored_packages:
        ignored_packages = []

    if not datas:
        datas = []

    if not env_vars:
        env_vars = {}

    root_path = validate_path(root_path) if root_path else PROJECT_PATHS.root

    # Try to recognize the structure of app
    build_path = root_path / "build"

    if not build_path.exists():
        build_path.mkdir(parents=True, exist_ok=True)

    # Remove last dist manually to avoid permission error if opened in some application
    dist_path = root_path / "dist"

    if dist_path.exists():
        try:
            shutil.rmtree(dist_path, ignore_errors=False)
        except (PermissionError, OSError) as remove_exception:

            raise PermissionError(
                mylogging.format_str(
                    "App is opened (May be in another app(terminal, explorer...)). Close it first."
                )
            ) from remove_exception

    # May be just name - not absolute
    main_file_path = Path(main_file)

    if not main_file_path.exists():

        # Iter paths and find the one
        main_file_path = find_path(
            main_file_path.name,
        )

        if not main_file_path.exists():
            raise KeyError("Main file not found, not inferred and must be configured in params...")

    main_file_path = main_file_path.resolve()

    if not name:
        name = main_file_path.stem

    main_folder_path = main_file_path.parent

    if icon:
        icon_path = Path(icon)

        if not icon_path.exists():

            # Iter paths and find the one
            icon_path = find_path(
                icon_path.name,
                exclude_names=["node_modules", "build"],
            )

            if not icon_path.exists():
                raise KeyError("Icon not found, not inferred check path or name...")

            icon_path = f"'{icon_path}'"
    else:
        icon_path = None

    generated_warning = """
#########################
### File is generated ###
#########################

# Do not edit this file, edit build_script
"""

    if remove_last_build:
        shutil.rmtree("build", ignore_errors=True)

    # Build JS to static asset
    if build_web is True or (build_web == "preset" and preset in ["eel"]):
        if verbosity:
            print("\n\nBuilding web.\n\n")

        gui_path = find_path("package.json").parent

        check_script_is_available(
            "npm", message="If building application with pyvueel, Node has to be installed."
        )

        terminal_do_command(
            "npm run build",
            cwd=gui_path.as_posix(),
            shell=True,
            verbose=verbose,
            error_header="Build of web files failed.",
        )

    if build_web or preset == "eel":
        if not web_path:
            web_path = find_path(
                "index.html",
                exclude_names=[
                    "public",
                    "node_modules",
                    "build",
                ],
            ).parent

        else:
            web_path = Path(web_path)

        if not web_path.exists():
            raise KeyError("Build web assets not found, not inferred and must be configured in params...")

        datas = [
            *datas,
            (web_path.as_posix(), "gui"),
        ]

    if preset == "eel":

        check_library_is_available("EelForkExcludeFiles")
        import EelForkExcludeFiles

        hidden_imports = [
            *hidden_imports,
            "EelForkExcludeFiles",
            "bottle_websocket",
        ]
        datas = [
            *datas,
            (
                EelForkExcludeFiles._eel_js_file,  # pylint: disable=protected-access
                "EelForkExcludeFiles",
            ),
        ]
        env_vars = {
            **env_vars,
            "MY_PYTHON_VUE_ENVIRONMENT": "production",
        }

    if env_vars:
        env_vars_template = f"""
{generated_warning}

import os
for i, j in {env_vars}.items():
    os.environ[i] = j
"""

        env_path = build_path / "env_vars.py"

        with open(env_path, "w") as env_vars_py:
            env_vars_py.write(env_vars_template)
        runtime_hooks = [env_path.as_posix()]
    else:
        env_path = None
        runtime_hooks = None

    spec_template = f"""
{generated_warning}

import sys
from pathlib import Path
import os

sys.setrecursionlimit(5000)
block_cipher = None

a = Analysis(['{main_file_path.as_posix()}'],
            pathex=['{main_folder_path.as_posix()}'],
            binaries=[],
            datas={datas},
            hiddenimports={hidden_imports},
            hookspath=[],
            runtime_hooks={runtime_hooks},
            excludes={ignored_packages},
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
            cipher=block_cipher)
exe = EXE(pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='{name}',
        debug={debug},
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console={console},
        icon={icon_path})
coll = COLLECT(exe,
            a.binaries,
            a.zipfiles,
            a.datas,
            strip=False,
            upx=True,
            upx_exclude=[],
            name='{name}')
"""
    spec_path = build_path / "app.spec"

    with open(spec_path, "w") as spec_file:
        spec_file.write(spec_template)

    spec_path = get_console_str_with_quotes(spec_path.as_posix())

    if virtualenv:
        my_venv = venvs.Venv(virtualenv)
        my_venv.create()
        if sync_requirements:
            my_venv.sync_requirements(sync_requirements)

        pyinstaller_script = my_venv.get_script_path("pyinstaller")
        command = my_venv.activate_command + " && " + pyinstaller_script + " --noconfirm " + spec_path

    else:
        command = f"pyinstaller --noconfirm {spec_path}"

    terminal_do_command(
        command,
        cwd=PROJECT_PATHS.root.as_posix(),
        shell=True,
        verbose=verbose,
        error_header="Build with pyinstaller failed. Troubleshooting: Try to install newest pyinstaller locally with "
        "'python setup.py install', update setuptools, delete 'build' and 'dist' folder and try again.",
    )

    if clean:
        to_delete = [spec_path] if not env_path else [spec_path, env_path]
        delete_files(to_delete)
