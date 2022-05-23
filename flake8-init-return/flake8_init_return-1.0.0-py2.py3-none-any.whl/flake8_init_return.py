from __future__ import annotations

import ast
import importlib.metadata
from typing import Any
from typing import Generator

MSG = 'FIR100 missing return value for initalizer'


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.assign_exprs: list[tuple[int, int]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if (
                isinstance(child, ast.FunctionDef)
                and child.name == '__init__' and child.returns is None
            ):
                self.assign_exprs.append((child.lineno, child.col_offset))
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib.metadata.version(__name__)

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        for line, col in visitor.assign_exprs:
            yield line, col, MSG, type(self)
