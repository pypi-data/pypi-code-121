"""
PIP handling for tiamat packaged python projects.
"""
import logging
import os
import pathlib
import sys
import tokenize
import traceback
from codeop import CommandCompiler
from types import CodeType
from typing import cast
from typing import List
from typing import Optional
from typing import Sequence
from typing import TextIO
from typing import Union

import pip._vendor.distlib
from pip._internal.cli.main import main as pip_main
from pip._internal.commands.install import InstallCommand
from pip._internal.commands.uninstall import UninstallCommand

from tiamatpip import configure
from tiamatpip.store import DistributionNotFound
from tiamatpip.store import Store
from tiamatpip.utils import debug_print
from tiamatpip.utils import patch_pip_internal_metadata_get_default_environment
from tiamatpip.utils import patched_environ
from tiamatpip.utils import patched_sys_argv


if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # We're running from a compiled pyinstaller binary and distlib knows
    # nothing about this. It also does not know how to handle pyimod03_importers, so,
    # we need to patch the __loader__ attribute to force distlib to it's fallback code.
    # This is particularly important on Windows where failing to do so makes tiamat-pip
    # unusable.
    pip._vendor.distlib.__loader__ = None


# If there are logging handlers already configured, then the basicConfig
# call below will be a no-op
logging.basicConfig(
    stream=sys.stderr,
    format="%(message)s",
    level=logging.DEBUG if "TIAMAT_PIP_DEBUG" in os.environ else logging.INFO,
)
log = logging.getLogger(__name__)


class Unbuffered:
    """
    Simple wrapper class to make the passed stream unbuffered.
    """

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        """
        Write data.
        """
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        """
        Write lines.
        """
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        """
        Return an attribute of the wrapped stream.
        """
        return getattr(self.stream, attr)


def should_redirect_argv(argv: List[str]) -> bool:
    """
    Check if ``argv`` should be redirected.
    """
    with debug_print("should_redirect_argv", argv):
        if "TIAMAT_PIP_INSTALL" in os.environ:
            # A pip command is already in progress. This is usually
            # hit when pip is building the dependencies of a package
            log.debug(
                "argv should be redirected to pip because TIAMAT_PIP_INSTALL "
                "was found on the environ"
            )
            return True
        pip_command_name = configure.get_pip_command_name()
        if len(argv) < 2:
            log.debug(
                "argv should not be redirected to pip because argv is smaller than expected: %s",
                argv,
            )
            return False
        elif argv[1] == pip_command_name:
            # We should intercept pip comands
            log.debug(
                "argv should be redirected to pip because argv[1]==%s", pip_command_name
            )
            return True
        log.debug(
            "argv should not be redirected to pip because 'argv[1](%s) != %s' and "
            "TIAMAT_PIP_INSTALL was not found in the environment",
            argv[1],
            pip_command_name,
        )
        # Do nothing
        return False


def process_argv(argv: List[str]) -> Optional[bool]:
    """
    Process ``argv`` if it looks like it should be processed.

    Does not return if argv is processed.

    If this function returns, we don't know how to execute the argv and did nothing.
    """
    # Disable any output buffering
    sys.stdout = cast(TextIO, Unbuffered(sys.stdout))
    sys.stderr = cast(TextIO, Unbuffered(sys.stderr))
    pypath = configure.get_user_base_path()
    assert pypath
    with debug_print(
        "process_argv", argv, pypath=pypath, pypath_exists=pypath.exists()
    ):
        if not should_redirect_argv(argv):
            raise Exception(
                "Please call `should_redirect_argv` before calling process_argv"
            )

        cpath = os.environ.get("CPATH") or None
        c_include_path = os.environ.get("C_INCLUDE_PATH") or None

        pyinstaller_extract_path = sys._MEIPASS  # type: ignore[attr-defined]
        included_python_headers_path = str(
            pathlib.Path(pyinstaller_extract_path).resolve() / "include" / "python"
        )
        if cpath is None:
            cpath = included_python_headers_path
        else:
            cpath_parts = cpath.split(os.pathsep)
            if included_python_headers_path not in cpath_parts:
                cpath_parts.append(included_python_headers_path)
            cpath = os.pathsep.join(cpath_parts)
        if c_include_path is None:
            c_include_path = included_python_headers_path
        else:
            c_include_path_parts = c_include_path.split(os.pathsep)
            if included_python_headers_path not in c_include_path_parts:
                c_include_path_parts.append(included_python_headers_path)
            c_include_path = os.pathsep.join(c_include_path_parts)
        with patched_environ(C_INCLUDE_PATH=c_include_path, CPATH=cpath):
            if argv[1] == "-c":
                # Example:
                #   python -c "print 'Foo!'"
                run_code(argv[2:])
            elif argv[1] == "-u" and argv[2] == "-c":
                # Example:
                #   python -u -c "print 'Foo!'"
                run_code(argv[3:])

            try:
                argv1_file = pathlib.Path(argv[1]).resolve()
                if argv1_file.is_file() and not str(argv1_file).endswith(
                    f"{os.sep}pip"
                ):
                    # Example:
                    #   python this-is-a-script.py arg1 arg2
                    run_python_file(argv[1:])
            except ValueError:
                # Not a valid file
                pass

            if argv[1] == "-m" and argv[2] == "pip":
                # Example:
                #   python -m pip install foo
                argv.pop(1)
            log.debug("argv before redirecting to pip: %s", argv)
            redirect_to_pip(argv)
            return True


def process_pip_argv(argv: List[str]) -> None:
    """
    Process pip ``argv``.
    """
    pypath = configure.get_user_base_path()
    assert pypath
    with debug_print(
        "process_pip_argv", argv, pypath=pypath, pypath_exists=pypath.exists()
    ):
        if pypath is None:
            raise RuntimeError(
                "You need to run 'tiamatpip.configure.set_user_base_path(<path>)' "
                "before calling tiamatpip.cli.process_pip_argv()"
            )

        if not pypath.is_dir():
            print(
                f"The path '{pypath}' does not exist or could not be created.",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)

        environ = {
            "TIAMAT_PIP_INSTALL": "1",
            "TIAMAT_PIP_PYPATH": str(pypath),
        }
        with patched_environ(environ=environ):
            process_argv(argv)


def redirect_to_pip(argv: List[str]) -> None:
    """
    Redirect ``argv`` to pip.
    """
    pypath = configure.get_user_base_path()
    assert pypath
    with debug_print(
        "redirect_to_pip", argv, pypath=pypath, pypath_exists=pypath.exists()
    ):
        targets: Sequence[str] = ("install", "list", "freeze", "uninstall", "frozen")
        try:
            cmd = argv[2]
        except IndexError:
            msg: str = "Must pass in available pip command, some of which are:"
            for cmd in targets:
                msg += f"\n - {cmd}"
            msg += (
                "\n\nIf you're missing a command which is supported by pip but not tiamat-pip "
                "please open a bug report."
            )
            print(msg, file=sys.stderr, flush=True)
            sys.exit(1)

        extra_environ = {
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }

        log.debug("Running the pip command '%s'", cmd)
        # Valid command found
        user_site_path = configure.get_user_site_path()

        if cmd in ("install", "uninstall"):
            include_in_store = True
        else:
            include_in_store = False
        if cmd == "install":
            args = [cmd]
            for arg in argv:
                if arg == "--prefix" or arg.startswith("--prefix="):
                    # When pip is building dependencies it might build them in isolation
                    # or pass --prefix.
                    # We should not inject our --target in this scnario
                    log.debug(f"Found '{arg}' in argv. Not adding our own target.")
                    # If the package is meant to be installed in our pypath, don't
                    # keep track of it in our store
                    include_in_store = False
                    break
            else:
                # Install into our custom site packages target path
                args.extend(["--target", str(user_site_path)])
        elif cmd == "uninstall":
            args = [cmd]
            patch_pip_internal_metadata_get_default_environment()
            extra_environ["TIAMAT_PIP_UNINSTALL"] = "1"
        elif cmd in ("list", "freeze"):
            args = [cmd, "--path", str(user_site_path)]
        elif cmd == "frozen":
            cmd = "list"
            args = [cmd]
        else:
            args = [cmd]
        args.extend(argv[3:])
        pkgs = []
        parser: Union[InstallCommand, UninstallCommand]
        if cmd in ("install", "uninstall"):
            if cmd == "install":
                parser = InstallCommand("name", "summary")
            else:
                parser = UninstallCommand("name", "summary")
            _, _args = parser.parse_args(args[:])
            pkgs.extend(_args[1:])
            log.debug(f"Packages to {cmd}: {pkgs}")

        # Call pip
        with patched_environ(environ=extra_environ):
            try:
                exitcode = call_pip(args)
                if include_in_store is True:
                    store = Store()
                    for pkg in pkgs:
                        try:
                            if cmd == "install":
                                store.add(pkg)
                            else:
                                store.remove(pkg)
                        except DistributionNotFound as exc:
                            print(str(exc), file=sys.stderr, flush=True)
                            exitcode = 1
                    store.write()
                sys.exit(exitcode)
            finally:
                pypath = configure.get_user_base_path()
                assert pypath
                debug_print(
                    "redirect_to_pip finally",
                    args,
                    pypath=pypath,
                    pypath_exists=pypath.exists(),
                )


def call_pip(argv: List[str]) -> int:
    """
    Call ``pip``.
    """
    with debug_print("call_pip", argv):
        exitcode: int = pip_main(argv)
        return exitcode


def _run_code(source, filename=None, exec_locals=None):
    if exec_locals is None:
        exec_locals = {"__name__": "__console__", "__doc__": None}
    if filename is None:
        filename = "<tiamat-pip-run-code>"
    else:
        # We want scripts which have an 'if __name__ == "__main__":'
        # section to run it.
        exec_locals["__name__"] = "__main__"
        exec_locals["__file__"] = filename

    compiler = CommandCompiler()
    try:
        code: Optional[CodeType] = compiler(source, filename, "exec")
    except (OverflowError, SyntaxError, ValueError):
        traceback.print_exc()
        sys.exit(1)

    assert code

    try:
        exec(code, exec_locals)
    except SystemExit as exc:
        if exc.code is not None:
            if isinstance(exc.code, str):
                print(exc.code, file=sys.stderr, flush=True)
                sys.exit(1)
            sys.exit(exc.code)
        sys.exit(1)
    except Exception:  # noqa: E722
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


def run_code(argv: List[str]) -> None:
    """
    Run a code string, emulating `python -c "..."`.

    Does not return.
    """
    source, *_ = argv
    with debug_print("run_code", argv):
        with patched_sys_argv(argv):
            # because we are emulating python execution, any errors here should be fatal
            _run_code(source)


def run_python_file(argv: List[str]) -> None:
    """
    Run a python file, emulating `python file.py`.

    Does not return.
    """
    with debug_print("run_python_file", argv):
        python_file, *_ = argv
        with tokenize.open(python_file) as rfh:
            source = rfh.read()
            with patched_sys_argv(argv):
                # We want scripts which have an 'if __name__ == "__main__":'
                # section to run it
                # because we are emulating python execution, any errors here should be fatal
                _run_code(source)
