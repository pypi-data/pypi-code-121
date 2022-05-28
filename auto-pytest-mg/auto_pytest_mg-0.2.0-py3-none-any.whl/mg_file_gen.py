import ast
import logging
from pathlib import Path

from auto_pytest_mg.mg_class import MGClass
from auto_pytest_mg.mg_function import MGFunction

logger = logging.getLogger(__name__)


def write_mg_test_file(file_path: Path) -> None:
    file_text = _generate_mg_test_file_text(file_path)
    mg_test_file_path = _get_mg_test_file_path(file_path)
    mg_test_file_path.write_text(file_text)
    logger.info(f"Created {mg_test_file_path.absolute()}")


def _ast_parse_file(file_path: Path) -> ast.AST:
    return ast.parse(file_path.read_text())


def _generate_mg_test_file_text(file_path: Path) -> str:
    node = _ast_parse_file(file_path)
    functions = [MGFunction(x) for x in node.body if isinstance(x, ast.FunctionDef)]
    classes = [MGClass(x) for x in node.body if isinstance(x, ast.ClassDef)]
    all_function_and_class_names = [*[f.name for f in functions], *[c.name for c in classes]]
    return "\n\n\n".join(
        [
            f"from {file_path.stem.replace('.py', '')} import {', '.join(all_function_and_class_names)}",
            *[class_.get_test_text() for class_ in classes],
            *[function.get_test_text() for function in functions],
        ]
    )


def _get_mg_test_file_path(file_path: Path) -> Path:
    stem = file_path.stem
    test_file_name = stem.replace(stem, f"test_{stem}.py")
    return Path(file_path.parent / test_file_name)
