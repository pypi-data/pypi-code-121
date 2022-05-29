from typing import List

import ast
from dataclasses import dataclass

import inflection

from auto_pytest_mg.static import INDENT


@dataclass
class MGImport:
    definition: ast.Import

    @property
    def name(self) -> str:
        return _get_import_names(self.definition.names)[0]

    def get_fixture_text(self) -> str:
        return _get_fixture_text(self.name)


@dataclass
class MGImportFrom:
    definition: ast.ImportFrom

    @property
    def imported_names(self) -> List[str]:
        return _get_import_names(self.definition.names)

    def get_fixtures_text(self) -> List[str]:
        return [_get_fixture_text(name) for name in self.imported_names]


def _get_import_names(names: List[ast.alias]) -> List[str]:
    return [name.asname if name.asname else name.name for name in names]


def _get_fixture_text(name: str) -> str:
    mock_name = f"mock_{inflection.underscore(name)}"
    return "\n".join(
        [
            "@pytest.fixture",
            f"def {mock_name}(mocker):",
            f'{INDENT}{mock_name}_ = mocker.patch(f"{{MODULE_PATH}}.{name}")',
            f"{INDENT}return {mock_name}_",
        ]
    )
