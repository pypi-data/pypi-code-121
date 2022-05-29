from typing import List, Optional

import ast
from dataclasses import dataclass

import inflection

from auto_pytest_mg.mg_function import MGFunction
from auto_pytest_mg.static import INDENT


@dataclass
class MGClass:
    definition: ast.ClassDef

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def mock_fixture_name(self) -> str:
        return f"{inflection.underscore(self.name)}"

    @property
    def arg_names(self) -> List[str]:
        names = []
        for node in self.definition.body:
            # Handle classes with class-level arguments (e.g. dataclasses)
            if isinstance(node, ast.AnnAssign):
                names.append(node.target.id)
            elif isinstance(node, ast.FunctionDef) and node.name == "__init__":
                names.extend(MGFunction(node, None).arg_names)

        return names

    @property
    def methods(self) -> List[MGFunction]:
        return [
            MGFunction(method, parent_class=self)
            for method in self.definition.body
            if isinstance(method, ast.FunctionDef)
        ]

    def get_fixture_text(self) -> str:
        lines = [
            "@pytest.fixture",
            f"def {self.mock_fixture_name}(mocker):",
        ]
        if not self.arg_names:
            lines.append(f"{INDENT}return {self.name}()")
        else:
            for arg in self.arg_names:
                lines.append(f"{INDENT}{arg} = mocker.MagicMock()")

            lines.append(f"{INDENT}return {self._get_class_instantiation()}")

        return "\n".join(lines)

    def get_test_text(self) -> str:
        class_definition = f"class Test{self.name}:"
        method_lines = []
        init_test_text = self._get__init__test_text()
        if init_test_text:
            method_lines.append(init_test_text)

        method_lines.extend(
            [
                method.get_method_test_text()
                for method in self.methods
                if not method.name == "__init__"
            ]
        )
        method_lines_separated = "\n\n".join(method_lines)
        return "\n".join([class_definition, method_lines_separated])

    def _get__init__test_text(self) -> Optional[str]:
        if not self.arg_names:
            return None

        function_definition = f"{INDENT}def test__init__(self, mocker):"
        arg_mocks = [f"{INDENT * 2}{arg_name} = mocker.MagicMock()" for arg_name in self.arg_names]
        class_instantiation = (
            f"{INDENT * 2}{self.mock_fixture_name}_ = {self._get_class_instantiation()}"
        )
        return "\n".join([function_definition, *arg_mocks, "", class_instantiation])

    def _get_class_instantiation(self) -> str:
        call_args = " ".join([f"{arg}={arg}," for arg in self.arg_names])
        call_args = call_args[:-1]  # remove trailing comma
        return f"{self.name}({call_args})"
