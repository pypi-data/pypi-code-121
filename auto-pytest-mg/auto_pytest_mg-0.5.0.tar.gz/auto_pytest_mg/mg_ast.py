from typing import List

import ast
import itertools
from dataclasses import dataclass
from pathlib import Path

from auto_pytest_mg.console import console
from auto_pytest_mg.mg_class import MGClass
from auto_pytest_mg.mg_function import MGFunction
from auto_pytest_mg.mg_import import MGImport, MGImportFrom


@dataclass
class MGAST:
    file_path: Path
    imports: List[MGImport]
    classes: List[MGClass]
    imports_from: List[MGImportFrom]
    functions: List[MGFunction]

    @classmethod
    def from_file(cls, file_path: Path) -> "MGAST":
        ast_ = ast.parse(file_path.read_text())
        functions = []
        classes = []
        imports = []
        imports_from = []
        for node in ast_.body:
            if isinstance(node, ast.Import):
                imports.append(MGImport(node))
            elif isinstance(node, ast.ImportFrom):
                imports_from.append(MGImportFrom(node))
            elif isinstance(node, ast.ClassDef):
                classes.append(MGClass(node))
            elif isinstance(node, ast.FunctionDef):
                functions.append(MGFunction(node))

        return cls(
            file_path=file_path,
            imports=imports,
            imports_from=imports_from,
            classes=classes,
            functions=functions,
        )

    def write_mg_test_file(self) -> None:
        self.mg_test_file_path.write_text(self.mg_test_file_text)
        console.print(f"Generated test file at [green]{self.mg_test_file_path.absolute()}[/green]")

    @property
    def mg_test_file_path(self) -> Path:
        stem = self.file_path.stem
        test_file_name = stem.replace(stem, f"test_{stem}.py")
        return Path(self.file_path.parent / test_file_name)

    @property
    def dotted_module_path(self) -> str:
        module_path_parts = ".".join(self.file_path.parts[:-1])
        module_name = self.file_path.stem.replace(".py", "")
        return f"{module_path_parts}.{module_name}"

    @property
    def mg_test_file_text(self) -> str:
        text_body = "\n\n\n".join(
            [
                self.import_lines_text,
                self.module_path_constant,
                *self.import_fixtures,
                *self.import_from_fixtures,
                *self.class_fixtures,
                *self.class_tests,
                *self.function_tests,
            ]
        )
        return f"{text_body}\n"

    @property
    def import_lines_text(self) -> str:
        all_function_and_class_names = [
            *[f.name for f in self.functions],
            *[c.name for c in self.classes],
        ]
        return (
            f"import pytest\n\n"
            f"from {self.dotted_module_path} import {', '.join(all_function_and_class_names)}"
        )

    @property
    def import_fixtures(self) -> List[str]:
        return [import_.get_fixture_text() for import_ in self.imports]

    @property
    def import_from_fixtures(self) -> List[str]:
        return list(
            itertools.chain(*[import_.get_fixtures_text() for import_ in self.imports_from])
        )

    @property
    def class_fixtures(self) -> List[str]:
        return [class_.get_fixture_text() for class_ in self.classes]

    @property
    def class_tests(self) -> List[str]:
        return [class_.get_test_text() for class_ in self.classes]

    @property
    def function_tests(self) -> List[str]:
        return [function.get_function_test_text() for function in self.functions]

    @property
    def module_path_constant(self) -> str:
        return f'MODULE_PATH = "{self.dotted_module_path}"'
