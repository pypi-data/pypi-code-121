import os
import sys
from dataclasses import dataclass
from importlib.machinery import ModuleSpec, PathFinder
from inspect import getattr_static, getcomments, getdoc, getmembers, isfunction
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

from .utils import inVenv, readEnvFile


class _UnsupportedCommand(Exception):
    pass


class _TaskError(Exception):
    pass


class _InternalError(Exception):
    pass


class _CustomFinder(PathFinder):
    """
    Allows us to import a file in the current diectory, that is
    the directory the file is run in. the tasks.py file should
    always be run from it's own dir, for now

    https://stackoverflow.com/a/44788410
    """

    _path = [os.getcwd()]

    @classmethod
    def find_spec(
        cls: Any, fullname: Any, path: Any = None, target: Any = None
    ) -> Optional[ModuleSpec]:
        return super().find_spec(fullname, cls._path, target)


sys.meta_path.append(_CustomFinder)  # type: ignore


def _dummy() -> bool:
    return True


@dataclass
class _Function:
    """Used to hold useful information on a function"""

    name: str = ""
    func: Callable[[], bool] = _dummy
    defaults: List[Any] = None  # type: ignore
    argnames: Optional[List[str]] = None


class _Taskr:
    def __init__(self, module: ModuleType) -> None:
        self.module = module
        self.funcs: Dict[str, _Function] = {}
        self._envs: Dict[str, str] = {}
        self._default: str = self._check_default()
        self._get_tasks()
        self._enforce_venv()
        self._check_env_var()

    def _check_env_var(self) -> None:
        """
        Reads in a user set environment file, and sets it when running a task
        """
        try:
            env_file = getattr_static(self.module, "ENVS")
            envs = readEnvFile(env_file)
            self._envs = envs
        except AttributeError:
            pass

    def _enforce_venv(self) -> None:
        """
        Looks to see if the tasks file requires the user to be in a venv
        """
        try:
            res = getattr_static(self.module, "VENV_REQUIRED")

            if res is not False and not inVenv():
                print("Not currently in a virtual environment, stopping")
                sys.exit(1)

        except AttributeError:
            pass

    def _check_default(self) -> str:
        """
        Runs a simple check for the efault keyword, and it a user sets it
        then mark it
        """
        try:
            return str(getattr_static(self.module, "DEFAULT"))
        except AttributeError:
            return ""

    def _get_tasks(self) -> None:
        """
        Internal function that pulls every function from a module
        and matches it with a name, basically the core
        """
        funcs = getmembers(self.module, isfunction)
        for func in funcs:
            if not func[0].startswith("_"):
                self.funcs[func[0]] = _Function(
                    name=func[0],
                    func=func[1],
                    defaults=func[1].__defaults__,
                    argnames=func[1].__code__.co_varnames[: func[1].__code__.co_argcount],
                )

    @staticmethod
    def init() -> None:
        """
        Generates a default task file
        """
        from taskr.template import template

        filename = "tasks.py"

        if os.path.exists(filename):
            print("Task file already exists, skipping generation")
            return

        with open(filename, "w") as file:
            file.write(template)

        print(f"Generated sample task file {filename}")

    def list(self) -> None:
        """
        Lists available tasks

        On initialization we get a dictionary of names to functions
        This will loop through the names, and try to grab the docstrings
        of the functions and display them

        If there is a default function defines, we mark it
        """
        if len(self.funcs) == 0:
            print("No functions defined or found")
            return

        print("\nTasks and arguments:")

        display = {}
        for name, func_attrs in self.funcs.items():
            if name == self._default:
                name = f"*{name}"

            if func_attrs.argnames:
                name = f"{name}: {', '.join(func_attrs.argnames)}"

            # Try to find documentation for the function
            doc = None
            docString = getdoc(func_attrs.func)  # Regular dock block
            docPreceed = getcomments(func_attrs.func)  # Single line doc above function
            if docPreceed:
                doc = docPreceed.replace("#", "").strip()
            if docString:
                doc = docString.replace("\n", "").strip()
            if not doc:
                doc = "No comment"

            display[name] = doc

        maxName = max(display.keys(), key=len)
        for name, doc in display.items():
            print(f" {name:<{len(maxName)+1}}: {doc}")

        print("\n* = default")

    def process(self, task: str, args: Optional[List[str]] = None) -> None:
        """
        Given a task name, runs the function if it exists
        If a task that takes arguments is passed
            - make sure that only the correct amount is passed
            - can allow no args passed
        If a task that takes no arguments is passed
            - ignore all args after it
        """
        known = self.funcs.get(task)
        if known:
            try:
                # Apply default env vars is user has them set
                # This happens before runners copies the systems envs, so
                # these are copied over
                # TODO - add tests?
                if self._envs:
                    for k, v in self._envs.items():
                        os.environ[k] = v
                if args and known.defaults:
                    if len(args) > len(known.defaults):
                        print("Warning - More arguments passed than task takes. Skipping")
                        return
                    known.func(*args)
                else:
                    known.func()
            except Exception as e:
                print(f"Error running task {task}: {e}")
        else:
            print(f"Unknown task: {task}")

    def hasDefault(self) -> bool:
        """
        Let's the CLI know if we can run a default command
        """
        return self._default != ""

    def default(self) -> bool:
        """
        Runs the default task, if it's defined
        """
        if self._default:
            if self._default not in self.funcs:
                print(f"Task {self._default} is not defined")
                return False

            self.funcs.get(self._default).func()  # type: ignore
            return True
        else:
            print("No default defined")
            return False
