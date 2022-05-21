"""Module with functions for 'project_paths' subpackage."""

from __future__ import annotations
from typing import Union
from pathlib import Path
import sys
import builtins

from mypythontools.paths import validate_path, find_path

PathLike = Union[Path, str]  # Path is included in PathLike
"""Str pr pathlib Path. It can be also relative to current working directory."""


class ProjectPaths:
    """Define paths for usual python projects like root path, docs path, init path etc.

    You can find paths, that are lazy evaluated only after you ask for them. They are inferred
    automatically, but if you have alternative structure, you can also set it. Getters return path objects,
    so it's posix.

    Note:
        If you use paths in `sys.path.insert` or as subprocess main parameter, do not forget to convert it
        to string with `as_posix()`.
    """

    def __init__(self) -> None:
        """Init the paths."""
        self._root = None
        self._app = None
        self._init = None
        self._tests = None
        self._docs = None
        self._readme = None

    def add_root_to_sys_path(self) -> None:
        """As name suggest, add root to sys.paths on index 0."""
        if self.root.as_posix() not in sys.path:
            sys.path.insert(0, self.root.as_posix())

    @property
    def root(self) -> Path:
        """Path where all project is (docs, tests...). Root is usually current working directory.

        Type:
            Path

        Default:
            Path.cwd()
        """
        # If not value yet, set it first
        if not self._root:
            new_root_path = Path.cwd()

            # If using jupyter notebook from tests - very specific use case
            if new_root_path.name == "tests" and hasattr(builtins, "__IPYTHON__"):
                new_root_path = new_root_path.parent

            self._root = new_root_path

        return self._root

    @root.setter
    def root(self, new_path: PathLike) -> None:
        self._root = validate_path(new_path)

    @property
    def init(self) -> Path:
        """Path to __init__.py.

        Type:
            Path

        Default:
            **/__init__.py
        """
        if not self._init:
            exclude = []
            for i in ["docs", "tests"]:
                try:
                    exclude.append(getattr(self, i))
                except AttributeError:
                    pass

            self._init = find_path(
                "__init__.py",
                self.root,
                exclude_paths=exclude,
            )

        return self._init

    @init.setter
    def init(self, new_path: PathLike) -> None:
        self._init = validate_path(new_path)

    @property
    def app(self) -> Path:
        """Folder where python scripts are (and __init__.py).

        Type:
            Path

        Default:
            __App_path
        """
        if not self._app:
            self._app = self.init.parent

        return self._app

    @app.setter
    def app(self, new_path: PathLike) -> None:
        self._app = validate_path(new_path)

    @property
    def tests(self) -> Path:
        """Folder where tests are stored. Usually root / tests.

        'test', 'Test', 'Tests', 'TEST', 'TESTS' also inferred if on root.

        Type:
            Path

        Default:
            root_path/tests
        """
        if not self._tests:
            for i in ["tests", "test", "Test", "Tests", "TEST", "TESTS"]:
                if (self.root / i).exists():
                    self._tests = self.root / i
                    return self._tests

            raise RuntimeError("Test path not found.")

        return self._tests

    @tests.setter
    def tests(self, new_path: PathLike) -> None:
        self._tests = validate_path(new_path)

    @property
    def docs(self) -> Path:
        """Where documentation is stored. Usually root / docs.

        'doc', 'Doc', 'Docs', 'DOC', 'DOCS' also inferred if on root.

        Type:
            Path

        Default:
            root_path/docs
        """
        if not self._docs:
            for i in ["docs", "doc", "Doc", "Docs", "DOC", "DOCS"]:
                if (self.root / i).exists():
                    self._docs = self.root / i
                    return self._docs

            raise RuntimeError("Test path not found.")

        return self._docs

    @docs.setter
    def docs(self, new_path: PathLike) -> None:
        self._docs = validate_path(new_path)

    @property
    def readme(self) -> Path:
        """Return README path whether it's capitalized or not.

        'Readme.md', 'readme.md', and rst extension also inferred if on root.

        Type:
            Path

        Default:
            root_path/README.md
        """
        if not self._readme:
            for i in ["README.md", "Readme.md", "readme.md", "README.rst", "Readme.rst", "readme.rst"]:
                if (self.root / i).exists():
                    self._readme = self.root / i
                    return self._readme
            raise RuntimeError("Readme path not found.")

        return self._readme

    @readme.setter
    def readme(self, new_path: PathLike) -> None:
        self._readme = validate_path(new_path)

    def reset_paths(self):
        """Reset all the paths to default."""
        self._root = None
        self._app = None
        self._init = None
        self._tests = None
        self._docs = None
        self._readme = None


PROJECT_PATHS = ProjectPaths()
