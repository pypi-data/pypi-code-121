"""Import tracker for python scripts

Search for all import statements using the python grammar[0] without having to
actually execute any code.

import_stmt     ::=  "import" module ["as" identifier] ("," module ["as" identifier])*
                 | "from" relative_module "import" identifier ["as" identifier]
                 ("," identifier ["as" identifier])*
                 | "from" relative_module "import" "(" identifier ["as" identifier]
                 ("," identifier ["as" identifier])* [","] ")"
                 | "from" relative_module "import" "*"
module          ::=  (identifier ".")* identifier
relative_module ::=  "."* module | "."+

[0] https://docs.python.org/3/reference/simple_stmts.html#import
"""
import argparse
import ast
import json
import sys
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import pytest

# The following modules are imported because I want to have relevant tests in
# the docstrings. They don't actually do anything.
try:
    import import_test_1  # pylint: disable=import-error, unused-import
except ModuleNotFoundError:
    pass
import import_checker.import_test_2  # pylint: disable=unused-import
from import_checker import import_test_3  # pylint: disable=unused-import
from import_checker.import_test_4 import (
    HelloWorld as hw4,  # pylint: disable=unused-import
)  # pylint: disable=unused-import
from import_checker.import_test_5 import import_test_5  # pylint: disable=unused-import
from import_checker.import_test_6.import_test_6 import (
    HelloWorld as hw6,  # pylint: disable=unused-import
)  # pylint: disable=unused-import

# The 'import <module>' imports:
# ==============================
# Import test 1:
#   name: module
#     library_dependencies: module
#     specific_submodules_imported: <None>
# Import test 2:
#   name: module.submodule
#     library_dependencies: module.submodule
#     specific_submodules_imported: <None>

# The 'from <module> import <thing>' imports:
# ===========================================
# Import test 3:
#   module: module, names: [submodule]
#     library_dependencies: module
#     specific_submodules_imported: module.submodule
# Import test 4:
#   module: module.submodule, names: [object]
#     library_dependencies: module.submodule
#     specific_submodules_imported: module.submodule.object
# Import test 5:
#   module: module.submodule, names: [submodule]
#     library_dependencies: module.submodule
#     specific_submodules_imported: module.submodule.submodule
# Import test 6:
#   module: module.submodule.submodule, names: [object]
#     library_dependencies: module.submodule.submodule
#     specific_submodules_imported: module.submodule.submodule.object


@dataclass
class PyFile:
    """Class to represent a python file
    >>> myfile = PyFile(__file__, depth_limit=0, include_stdlib_modules=True)
    >>> print(json.dumps(myfile.get_dependencies()[__file__]['library_dependencies'], indent=4))
    [
        "argparse",
        "ast",
        "dataclasses",
        "import_checker",
        "import_checker.import_test_2",
        "import_checker.import_test_4",
        "import_checker.import_test_5",
        "import_checker.import_test_6.import_test_6",
        "import_test_1",
        "json",
        "pathlib",
        "pytest",
        "sys",
        "typing"
    ]
    >>> no_stdlib_file = PyFile(__file__, depth_limit=0, include_stdlib_modules=False)
    >>> print(json.dumps(no_stdlib_file.get_dependencies()[__file__]['library_dependencies'], indent=4))
    [
        "import_checker",
        "import_checker.import_test_2",
        "import_checker.import_test_4",
        "import_checker.import_test_5",
        "import_checker.import_test_6.import_test_6",
        "import_test_1",
        "pytest"
    ]
    >>> myfile.get_dependencies()[__file__]['specific_submodules_imported'] == no_stdlib_file.get_dependencies()[__file__]['specific_submodules_imported']
    True
    """

    path: Path
    depth: int = 0
    depth_limit: int = 1
    include_stdlib_modules: bool = True
    library_dependencies: Set = field(default_factory=set)
    specific_submodules_imported: Set = field(default_factory=set)
    imported_files: Dict[str, Any] = field(default_factory=dict)
    _raw_import: List[ast.Import] = field(default_factory=list)
    _raw_importfrom: List[ast.ImportFrom] = field(default_factory=list)

    def __post_init__(self):
        self.path = Path(self.path).expanduser()
        self.resolve_dependencies()

    def _add_library_dependency(self, name):
        """Add dependency, with caveats

        >>> no_stdlib = PyFile(__file__, depth_limit=0, include_stdlib_modules=False)
        >>> no_stdlib._add_library_dependency('zipapp')
        >>> no_stdlib._add_library_dependency('ast')
        >>> no_stdlib._add_library_dependency('csv')
        >>> no_stdlib._add_library_dependency('hashlib')
        >>> print(json.dumps(no_stdlib.get_dependencies()[__file__]['library_dependencies'], indent=4))
        [
            "import_checker",
            "import_checker.import_test_2",
            "import_checker.import_test_4",
            "import_checker.import_test_5",
            "import_checker.import_test_6.import_test_6",
            "import_test_1",
            "pytest"
        ]
        """
        # if we're including stdlib modules, just add the dependency
        if self.include_stdlib_modules:
            self.library_dependencies.add(name)
        # if we're not including stdlib modules, maybe don't
        elif not self.include_stdlib_modules:
            # sys.stdlib_module_names is new in python 3.10
            # https://docs.python.org/3/library/sys.html#sys.stdlib_module_names
            if name in sys.stdlib_module_names:
                pass
            else:
                self.library_dependencies.add(name)

    def resolve_dependencies(self):
        """Resolve the dependencies of this file

        Also, attempt to gather the dependencies of files this one imports.

        Note: DO THIS STATICALLY. WITHOUT ACTUALLY IMPORTING ANY MODULES.
        """
        with self.path.open("r", encoding="utf-8") as readfile:
            ast_module = ast.parse(readfile.read(), str(self.path))
        for item in ast.walk(ast_module):
            if isinstance(item, ast.Import):
                self.process_import(item)
                self._raw_import.append(item)
            elif isinstance(item, ast.ImportFrom):
                for _name in item.names:
                    self._add_library_dependency(item.module)
                self.process_importfrom(item)
                self._raw_importfrom.append(item)

        if self.depth == self.depth_limit:
            return

        self.resolve_recursive_dependencies()

    def resolve_recursive_dependencies(self):
        # We only check recursive dependencies in files that can be
        # found somewhere in this directory.

        # NOTE: this is only static analysis, and is most likely not 100% compatible
        # with what the import module actually does wrt searching sys.PATH.
        # hashtag-best-effort

        # Check all the modules from library_dependencies.
        for module in self.library_dependencies:
            if module not in sys.stdlib_module_names:
                try:
                    # Check relative to the file itself. Examples:
                    #   - import import_test_1
                    if Path(self.path.parent / f"{module}.py").exists():
                        new_module = Path(self.path.parent / f"{module}.py")
                    # Check relative to the directory import_checker is running from.
                    # This assumes that the module is in a similarly-named folder
                    # and one is running import_checker from the root. Examples:
                    #   - import import_checker.import_test_2
                    #   - from import_checker.import_test_4 import HelloWorld

                    # The reason why the latter works like the former is that
                    # both the above statements import a module named
                    # "import_checker.import_test_X"
                    elif Path(f"{module.replace('.', '/')}.py").exists():
                        new_module = Path(f"{module.replace('.', '/')}.py")
                    else:
                        continue
                    self.imported_files[str(new_module)] = PyFile(
                        path=new_module,
                        depth=self.depth + 1,
                        depth_limit=self.depth_limit,
                        include_stdlib_modules=self.include_stdlib_modules,
                    )
                except Exception as err:
                    raise err

        for submodule in self.specific_submodules_imported:
            if submodule not in sys.stdlib_module_names:
                # Handle the case:
                #   - from import_checker import import_test_3
                new_module = Path(f"{submodule.replace('.', '/')}.py")
                if new_module.exists() and not new_module.is_dir():
                    self.imported_files[str(new_module)] = PyFile(
                        path=new_module,
                        depth=self.depth + 1,
                        depth_limit=self.depth_limit,
                        include_stdlib_modules=self.include_stdlib_modules,
                    )

    def process_import(self, ast_import: ast.Import):
        for name in ast_import.names:
            self._add_library_dependency(name.name)

    def process_importfrom(self, ast_importfrom: ast.ImportFrom):
        # these should be the same, but self.library_dependencies is a set
        # so add it anyway
        for name in ast_importfrom.names:
            self._add_library_dependency(ast_importfrom.module)

        for name in ast_importfrom.names:
            self.specific_submodules_imported.add(
                f"{ast_importfrom.module}.{name.name}"
            )

    def get_dependencies(
        self, dependencies: Optional[Dict[str, Dict[str, List[str]]]] = None
    ):
        """Recursively grab dependencies of this and all imported files"""
        deps: Dict[str, Dict[str, List[str]]] = {}
        if dependencies is not None:
            deps = dependencies

        if str(self.path) not in deps:
            deps[str(self.path)] = {}

        deps[str(self.path)]["library_dependencies"] = sorted(
            list(self.library_dependencies)
        )
        deps[str(self.path)]["specific_submodules_imported"] = sorted(
            list(self.specific_submodules_imported)
        )
        for _module, pyfile in self.imported_files.items():
            pyfile.get_dependencies(dependencies=deps)
        return deps


def parse_imports(path: List[str], depth: int, ignore_stdlib: bool) -> int:
    dependencies: Dict[str, Dict[str, List[str]]] = {}
    for item in path:
        pyfile = PyFile(
            Path(item).expanduser(),
            depth_limit=depth,
            include_stdlib_modules=ignore_stdlib,
        )
        pyfile.get_dependencies(dependencies=dependencies)
    print(json.dumps(dependencies, indent=4))
    return 0


def test():
    """Run tests

    >>> print('I like doctests! Good for ad-hoc or small-file tests')
    I like doctests! Good for ad-hoc or small-file tests
    """
    return pytest.main([__file__, "--doctest-modules"])


def satisfy_pylint():
    # Despite flagging certain imports as
    # pylint: disable=unused-import
    # some of them (namely the hw4 and hw6 imports) are still being flagged
    # during the linting process. As a result, use them here.
    # This function is a no-op and should be removed once I figure out why
    # pylint isn't working.
    helloworld4 = hw4(foobar="hmmmm")
    helloworld6 = hw6(foobar="i wonder why pylint does this")
    return helloworld4, helloworld6


def main():
    """main"""
    main_parser = argparse.ArgumentParser()
    main_parser.set_defaults(
        run=lambda: main_parser.print_help()  # pylint: disable=unnecessary-lambda
    )
    modes = main_parser.add_subparsers(title="Mode", metavar="")

    cli_parser = modes.add_parser("cli", help="Use the import checker as a CLI tool")
    cli_parser.add_argument(
        "-p", "--path", help="File(s) to start at", type=str, required=True, nargs="+"
    )
    cli_parser.add_argument(
        "-d", "--depth", help="How far to recurse", type=int, default=100
    )
    cli_parser.add_argument(
        "-i",
        "--ignore_stdlib",
        help="Whether or not to ignore the stdlib",
        action="store_false",
    )
    cli_parser.set_defaults(run=parse_imports)

    cli_parser = modes.add_parser("test", help="Run the tests")
    cli_parser.set_defaults(run=test)

    args = main_parser.parse_args()

    return args.run(**{key: value for key, value in vars(args).items() if key != "run"})


if __name__ == "__main__":
    sys.exit(main())
