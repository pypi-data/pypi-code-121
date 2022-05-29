from typing import TYPE_CHECKING, List, Optional

import ast
from dataclasses import dataclass

from auto_pytest_mg.static import INDENT

if TYPE_CHECKING:
    from auto_pytest_mg import mg_class


@dataclass
class MGFunction:
    definition: ast.FunctionDef
    parent_class: Optional["mg_class.MGClass"] = None

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def is_method(self) -> bool:
        return self.parent_class is not None

    @property
    def is_property(self) -> bool:
        for decorator in self.definition.decorator_list:
            try:
                if decorator.id in {"property", "cached_property"}:
                    return True
            except AttributeError:
                continue

        return False

    @property
    def arg_names(self) -> List[str]:
        return [arg.arg for arg in self.definition.args.args if arg.arg not in {"self", "cls"}]

    def get_method_test_text(self) -> str:
        if not self.is_method:
            return ""
        function_definition = f"{INDENT}def test_{self.name}(self, mocker, mg, {self.parent_class.mock_fixture_name}):"  # type: ignore
        asert_obj = f"{self.parent_class.mock_fixture_name}.{self.name}"  # type: ignore
        function_body_lines = self._get_function_body_lines(asert_obj, INDENT * 2)
        return self._get_function_text(function_definition, function_body_lines)

    def get_function_test_text(self) -> str:
        function_definition = f"def test_{self.name}(mocker, mg):"
        asert_obj = self.name
        function_body_lines = self._get_function_body_lines(asert_obj, INDENT)
        return self._get_function_text(function_definition, function_body_lines)

    def _get_arrange_variable_lines(self):
        return [f"{arg_name} = mocker.MagicMock()" for arg_name in self.arg_names]

    def _get_function_call_line(self) -> str:
        asert_obj = (
            f"{self.parent_class.mock_fixture_name}.{self.name}" if self.is_method else self.name  # type: ignore
        )
        call_args = " ".join([f"{arg}={arg}," for arg in self.arg_names])
        call_args = call_args[:-1]  # remove trailing comma
        function_call = "" if self.is_property else f"({call_args})"
        return f"result = {asert_obj}{function_call}"

    def _get_function_body_lines(self, assert_obj: str, indent: str) -> List[str]:
        return [
            f"{indent}{line}" if line else ""
            for line in [
                *self._get_arrange_variable_lines(),
                f"mg.generate_uut_mocks_with_asserts({assert_obj})",
                "",
                self._get_function_call_line(),
            ]
        ]

    def _get_function_text(self, function_definition: str, function_body_lines: List[str]) -> str:
        return "\n".join([function_definition, *function_body_lines])
