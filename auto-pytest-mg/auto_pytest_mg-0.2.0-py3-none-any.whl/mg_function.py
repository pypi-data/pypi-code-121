from typing import Any, Dict, List, Optional

import ast
from dataclasses import dataclass
from functools import cached_property

import inflection

INDENT = "    "


@dataclass
class MGFunction:
    definition: ast.FunctionDef
    parent_class: Optional[ast.ClassDef] = None

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def is_method(self) -> bool:
        return self.parent_class is not None

    @property
    def is_property(self) -> bool:
        for decorator in self.definition.decorator_list:
            if decorator.id in {"property", "cached_property"}:
                return True
        return False

    @cached_property
    def arg_name_to_annotation(self) -> Dict[str, ast.Name]:
        return {
            arg.arg: arg.annotation if arg.annotation else None
            for arg in self.definition.args.args
            if arg.arg not in {"self", "cls"}
        }

    @property
    def arg_names(self) -> List[str]:
        return list(self.arg_name_to_annotation.keys())

    @property
    def class_instance_variable(self) -> str:
        return f"{inflection.underscore(self.parent_class.name)}"

    def get_test_text(self) -> str:
        if not self.is_method:
            function_definition = f"def test_{self.name}(mocker, mg):"
        else:
            function_definition = f"{INDENT}def test_{self.name}(self, mocker, mg):"

        if self.is_method:
            asert_obj = f"{self.class_instance_variable}.{self.name}"
        else:
            asert_obj = self.name

        indent = INDENT * 2 if self.is_method else INDENT
        function_body_lines = [
            f"{indent}{line}"
            for line in [
                *self._get_arrange_variable_lines(),
                f"mg.generate_uut_mocks_with_asserts({asert_obj})",
                "",
                self._get_function_call_line(),
            ]
        ]
        if self.is_method:
            function_body_lines.insert(
                0,
                f"{indent}{self.class_instance_variable} = mocker.MagicMock(spec={self.parent_class.name})",
            )
        return "\n".join([function_definition, *function_body_lines])

    def _get_arrange_variable_lines(self):
        variable_lines = []
        for arg_name, annotation in self.arg_name_to_annotation.items():
            type_ = annotation.id if annotation else None
            if type_:
                mock = f"mocker.MagicMock(spec={type_})"
            else:
                mock = f"mocker.MagicMock()"

            variable_lines.append(f"{arg_name} = {mock}")

        return variable_lines

    def _get_function_call_line(self) -> str:
        if self.is_method:
            asert_obj = f"{self.class_instance_variable}.{self.name}"
        else:
            asert_obj = self.name

        if self.is_property:
            function_call = ""
        else:
            function_call = f"({', '.join(self.arg_names)})"

        return f"result = {asert_obj}{function_call}"
