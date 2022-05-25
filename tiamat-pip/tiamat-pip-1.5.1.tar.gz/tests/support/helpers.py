import json
import logging
import os
import pathlib
import random
import shutil
import string
import subprocess
import sys
import textwrap
from typing import List
from typing import Optional

import attr
import PyInstaller

import tiamatpip
from tiamatpip.store import parse_package_name
from tiamatpip.store import Store

log = logging.getLogger(__name__)

CODE_ROOT = pathlib.Path(tiamatpip.__file__).resolve().parent.parent


def random_string(
    prefix: str,
    size: int = 6,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
) -> str:
    """
    Generates a random string.

    :keyword str prefix: The prefix for the random string
    :keyword int size: The size of the random string
    :keyword bool uppercase: If true, include upper-cased ascii chars in choice sample
    :keyword bool lowercase: If true, include lower-cased ascii chars in choice sample
    :keyword bool digits: If true, include digits in choice sample
    :return str: The random string
    """
    if not any([uppercase, lowercase, digits]):
        raise RuntimeError(
            "At least one of 'uppercase', 'lowercase' or 'digits' needs to be true"
        )
    choices: List[str] = []
    if uppercase:
        choices.extend(string.ascii_uppercase)
    if lowercase:
        choices.extend(string.ascii_lowercase)
    if digits:
        choices.extend(string.digits)

    return prefix + "".join(random.choice(choices) for _ in range(size))


@attr.s(frozen=True)
class ProcessResult:
    """
    This wrapper around a subprocess result.

    This class serves the purpose of having a common result class which will hold the
    resulting data from a subprocess command.
    """

    exitcode = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()
    cmdline = attr.ib(default=None, kw_only=True)

    @exitcode.validator
    def _validate_exitcode(self, attribute, value):
        if not isinstance(value, int):
            raise ValueError(f"'exitcode' needs to be an integer, not '{type(value)}'")

    def __str__(self):
        message = self.__class__.__name__
        if self.cmdline:
            message += f"\n Command Line: {self.cmdline}"
        if self.exitcode is not None:
            message += f"\n Exitcode: {self.exitcode}"
        if self.stdout.strip() or self.stderr.strip():
            message += "\n Process Output:"
        if self.stdout.strip():
            message += f"\n   >>>>> STDOUT >>>>>\n{self.stdout}\n   <<<<< STDOUT <<<<<"
        if self.stderr.strip():
            message += f"\n   >>>>> STDERR >>>>>\n{self.stderr}\n   <<<<< STDERR <<<<<"
        return message + "\n"


@attr.s(kw_only=True, slots=True)
class TiamatPipProject:
    name: str = attr.ib()
    path: pathlib.Path = attr.ib()
    pypath: Optional[pathlib.Path] = attr.ib(init=False)
    build_conf_contents: str = attr.ib()
    run_py_contents: str = attr.ib()
    requirements: List[str] = attr.ib(default=attr.Factory(list))
    requirements_txt_contents: str = attr.ib()
    build_conf: pathlib.Path = attr.ib(init=False)
    run_py: Optional[pathlib.Path] = attr.ib(init=False)
    requirements_txt: Optional[pathlib.Path] = attr.ib(init=False)

    @name.default
    def _default_name(self) -> str:
        return random_string("project-")

    @pypath.default
    def _default_pypath(self) -> pathlib.Path:
        pypath = self.path / "pypath"
        pypath.mkdir(parents=True, exist_ok=True, mode=0o755)
        return pypath

    @build_conf.default
    def _default_build_conf(self) -> pathlib.Path:
        return self.path / "build.conf"

    @build_conf_contents.default
    def _default_build_conf_contents(self) -> str:
        if sys.platform.startswith("win"):
            pyinstaller_version = "dev"
        else:
            pyinstaller_version = PyInstaller.__version__
        return textwrap.dedent(
            """\
        tiamat:
          name: {}
          pyinstaller_version: "{}"
          dev_pyinstaller: False
        """.format(
                self.name,
                pyinstaller_version,
            )
        )

    @run_py.default
    def _default_run_py(self) -> pathlib.Path:
        return self.path / "run.py"

    @run_py_contents.default
    def _default_run_py_contents(self) -> str:
        return textwrap.dedent(
            """\
            #!/usr/bin/env python3

            import os
            import sys
            import traceback
            import multiprocessing
            import tiamatpip.cli
            import tiamatpip.configure


            tiamatpip.configure.set_user_base_path({!r})

            def main(argv):
                if argv[1] == "shell":
                    py_shell()
                    return
                if tiamatpip.cli.should_redirect_argv(argv):
                    tiamatpip.cli.process_pip_argv(argv)

                # If we reached this far, it means we're not handling pip stuff

                if argv[1] == "test":
                    print("Tested!")
                if argv[1] == "code":
                    tiamatpip.cli._run_code(sys.argv[2])
                else:
                    print("No command?!")

                sys.exit(0)


            def py_shell():
                import readline  # optional, will allow Up/Down/History in the console
                import code

                variables = globals().copy()
                variables.update(locals())
                shell = code.InteractiveConsole(variables)
                shell.interact()

            if __name__ == "__main__":
                if sys.platform.startswith("win"):
                    multiprocessing.freeze_support()
                main(sys.argv)
            """.format(
                str(self.pypath)
            )
        )

    @requirements_txt.default
    def _default_requirements_txt(self) -> pathlib.Path:
        return self.path / "requirements.txt"

    @requirements_txt_contents.default
    def _default_requirements_txt_contents(self) -> str:
        return "\n".join([str(CODE_ROOT)] + list(self.requirements))

    def __attrs_post_init__(self) -> None:
        self.build_conf.write_text(self.build_conf_contents)
        assert self.run_py
        self.run_py.write_text(self.run_py_contents)
        assert self.requirements_txt
        self.requirements_txt.write_text(self.requirements_txt_contents)

    @property
    def generated_binary_path(self) -> pathlib.Path:
        binary_path = self.path / "dist" / self.name
        if sys.platform.startswith("win"):
            return binary_path.with_suffix(".exe")
        return binary_path

    def copy_generated_project_to(self, path: pathlib.Path) -> None:
        dst = path / self.generated_binary_path.name
        log.info("Copying %s -> %s", self.generated_binary_path, dst)
        if self.generated_binary_path.is_dir():
            shutil.copytree(self.generated_binary_path, dst)
        else:
            shutil.copyfile(self.generated_binary_path, dst)

    def run(self, *args, cwd=None, check=None, **kwargs) -> ProcessResult:
        if cwd is None:
            cwd = str(self.path)

        generated_binary_path = self.generated_binary_path
        if not sys.platform.startswith("win"):
            # Only use relative paths on non Windows platforms
            generated_binary_path = generated_binary_path.relative_to(self.path)

        log.info(
            "Generated binary path: %s",
            generated_binary_path,
        )
        # Create the cmdline to run
        cmdline = [str(generated_binary_path)] + list(args)

        env = os.environ.copy()
        env["TIAMAT_PIP_DEBUG"] = "1"
        result = subprocess.run(
            cmdline,
            cwd=cwd,
            env=env,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            **kwargs,
        )
        ret = ProcessResult(
            result.returncode,
            result.stdout,
            result.stderr,
            cmdline=args,
        )
        if ret.exitcode == 0:
            log.debug(ret)
        else:
            log.error(ret)
        if check is True:
            result.check_returncode()
        return ret

    def run_code(self, code: str) -> ProcessResult:
        if code.startswith("\n"):
            code = code[1:]
        code = textwrap.dedent(code)
        return self.run("code", code)

    def build(self) -> None:
        cmdline = ["tiamat", "--log-level=debug", "build", "-c", "build.conf"]
        result = subprocess.run(
            cmdline,
            cwd=self.path,
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        ret = ProcessResult(
            result.returncode,
            result.stdout,
            result.stderr,
            cmdline=cmdline,
        )
        if ret.exitcode == 0:
            log.debug(ret)
        else:
            log.error(ret)
        result.check_returncode()
        log.info("%s was successfuly built!", self.name)

    def delete_pypath(self) -> None:
        assert self.pypath
        if self.pypath.exists():
            shutil.rmtree(self.pypath, ignore_errors=True)

    def get_store(self) -> Store:
        return Store(pypath=self.pypath)

    def get_installed_packages(self, include_frozen=False):
        data = {}
        if include_frozen:
            ret = self.run("pip", "frozen", "--format", "json")
            for pkginfo in json.loads(ret.stdout):
                data[parse_package_name(pkginfo["name"])] = pkginfo["version"]
        ret = self.run("pip", "list", "--format", "json")
        for pkginfo in json.loads(ret.stdout):
            data[parse_package_name(pkginfo["name"])] = pkginfo["version"]
        return data

    def __enter__(self):
        self.build()
        return self

    def __exit__(self, *args):
        shutil.rmtree(self.path, ignore_errors=True)
