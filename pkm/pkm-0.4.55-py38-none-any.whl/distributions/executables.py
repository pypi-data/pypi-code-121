import os
import stat
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pkm.api.distributions.distinfo import EntryPoint
from pkm.launchers import build_windows_script_launcher

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment


class Executables:

    @staticmethod
    def patch_shabang_for_interpreter(source: Path, target: Path, interpreter_path: Path):
        """
        copy the `source` script to the `target` path, patching the shabng line so that it will be executable
        under the given `env`
        :param source: path to the source script
        :param target: path to put the patched script
        :param interpreter_path: the interpreter which the patched script should be executeable with
        """
        with source.open('rb') as script_fd, target.open('wb+') as target_fd:
            first_line = script_fd.readline()
            if first_line.startswith(b"#!python"):
                w = 'w' if first_line.startswith(b"#!pythonw") else ''
                target_fd.write(
                    f"#!{interpreter_path.absolute()}{w}{os.linesep}".encode(sys.getfilesystemencoding()))
            else:
                target_fd.write(first_line)

            target_fd.write(script_fd.read())

        st = os.stat(source)
        os.chmod(target, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def generate(env: "Environment", target_dir: Path, file_name: str, script: str, is_gui: bool = False):
        """
        generates executable for the given `script` that is runnable under the given environment
        :param env: the environment to be used by the generated executable
        :param target_dir: where to put the executable
        :param file_name: the base name of the script to create (extension may vary)
        :param script: the script content to execute
        :param is_gui: if True, and in windows platform, will create a "gui" script, defaults to False.
        :return: path to the created executable
        """

        if env.operating_platform.has_windows_os():
            return build_windows_script_launcher(env, target_dir, file_name, script, is_gui)
        else:
            source = f"#!{env.interpreter_path.absolute()}\n{script}"

            result_script_path = target_dir / file_name
            result_script_path.write_text(source)

            st = os.stat(result_script_path)
            os.chmod(result_script_path, st.st_mode | stat.S_IEXEC)
            return result_script_path

    @staticmethod
    def generate_for_entrypoint(env: "Environment", entrypoint: EntryPoint, target_dir: Path) -> Path:
        """
        generates executable for the given entrypoint that is runnable under the given environment
        :param entrypoint: the entrypoint to generate the executable for
        :param env: the environment to be used by the generated executable
        :param target_dir: where to put the executable
        :return: path to the created executable
        """

        return Executables.generate(
            env, target_dir, entrypoint.name, entrypoint.ref.execution_script_snippet(),
            entrypoint.group == EntryPoint.G_CONSOLE_SCRIPTS)
