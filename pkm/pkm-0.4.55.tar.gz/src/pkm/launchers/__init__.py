"""
launchers are taken from:
https://bitbucket.org/vinay.sajip/simple_launcher
"""
import importlib.resources as resources
from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile

from pkm.api.distributions.distinfo import EntryPoint

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment


def build_windows_script_launcher(
        env: "Environment", target_dir: Path, file_name: str, script: str, is_gui: bool = False) -> Path:
    """
        creates windows launcher for the given `script` that is suitable to the os of the given environment.
        the launcher will be written into a file named `script_name` under the given `dir`

        :param env: the environment the created executable should use to run the script
        :param target_dir: the directory where to put the launcher in
        :param script: in case this argument is given it will be used as the script for the entrypoint,
               otherwise the script will be generated from the entrypoint object reference
        :param file_name: the base name of the executable file to create
                          (this name will be used for the file, but its extension may vary)
        :param is_gui: if True, will create a gui based launcher, defaults to False.
        :return: path to the created launcher
        """

    op_plat = env.operating_platform
    arch_suffix = '-arm' if op_plat.has_arm_cpu() else ''
    launcher_kind = 't' if is_gui else 'w'
    launcher_name = f"{launcher_kind}{arch_suffix}{op_plat.os_bits}.exe"

    launcher_data = resources.read_binary('pkm.launchers', launcher_name)

    result_file = target_dir / f"{file_name}.exe"
    with result_file.open('wb') as result_fd:
        result_fd.write(launcher_data)
        result_fd.write(f"#!{env.interpreter_path.absolute()}\r\n".encode())
        with ZipFile(result_fd) as result_zip_fd:
            result_zip_fd.writestr("__main__.py", script.encode())

    return result_file


def build_windows_entrypoint_launcher(
        env: "Environment",
        entrypoint: EntryPoint, target_dir: Path) -> Path:
    """
    creates windows launcher for the given `entrypoint` that is suitable to the os of the given environment.
    the launcher will be written into a file named `entrypoint.name` under the given `dir`

    :param env: the environment the created executable should use to run the script
    :param entrypoint: the entrypoint to create a script for
    :param target_dir: the directory where to put the launcher in
    :return: path to the created launcher
    """

    return build_windows_script_launcher(
        env, target_dir, entrypoint.name, entrypoint.ref.execution_script_snippet(),
        entrypoint.group == EntryPoint.G_CONSOLE_SCRIPTS
    )
