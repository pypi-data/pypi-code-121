# type: ignore[attr-defined]
from typing import List

import ast
from dataclasses import dataclass

from auto_pytest_mg.mg_function import MGFunction


@dataclass
class MGClass:
    definition: ast.ClassDef

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def methods(self) -> List[MGFunction]:
        return [
            MGFunction(method, parent_class=self.definition)
            for method in self.definition.body
            if isinstance(method, ast.FunctionDef)
        ]

    def get_test_text(self) -> str:
        class_definition = f"class Test{self.name}:"
        method_lines = [method.get_test_text() for method in self.methods]
        method_lines_separated = "\n\n".join(method_lines)
        return "\n".join([class_definition, method_lines_separated])
