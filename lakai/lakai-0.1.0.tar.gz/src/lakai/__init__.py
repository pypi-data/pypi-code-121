import dataclasses
import enum
import io
import sys
from typing import Any, Callable, Generic, List, Optional, TextIO, TypeVar

import lark
import lark.exceptions
import lark.lark as _lark
import lark.lexer
import lark.tree
import pkg_resources

__version__ = "0.1.0"
__all__ = [
    "Parser",
    "Lakai",
    "Leaf",
    "Node",
    "from_string",
    "from_resource",
    "pformat",
    "pprint",
]

T = TypeVar("T")
_LarkErrorHandler = Callable[[lark.exceptions.UnexpectedInput], bool]


class Parser(enum.Enum):
    EARLEY = enum.auto()
    LALR = enum.auto()
    CYK = enum.auto()


class Lakai:
    lark: _lark.Lark

    def __init__(self, lark: _lark.Lark) -> None:
        self.lark = lark

    def parse(
        self, text: str, start: Optional[str] = None, on_error: Optional[_LarkErrorHandler] = None
    ) -> "Node[Leaf]":
        return convert_lark_tree(self.lark.parse(text, start, on_error))


class Transformer:
    def visit(self, element: "Leaf | Node[Any]") -> Any:
        if isinstance(element, Node):
            name = element.name
            for index, child in enumerate(element.children):
                element.children[index] = self.visit(child)
        else:
            name = element.type
        method = getattr(self, f"visit_{name}", None)
        if method is not None:
            return method(element)
        return self.generic_visit(element)

    def generic_visit(self, element: "Leaf | Node[Any]") -> Any:
        return element


@dataclasses.dataclass
class Leaf:
    type: str
    value: str
    line: int
    column: int
    end_line: int = dataclasses.field(repr=False)
    end_column: int = dataclasses.field(repr=False)

    def __len__(self) -> int:
        return len(self.value)


@dataclasses.dataclass
class Node(Generic[T]):
    name: str
    children: List["T | Node[T]"]


def convert_lark_tree(tree: lark.tree.ParseTree) -> Node[Leaf]:
    """Converts a Lark tree to a Lakai tree."""

    children: List["Leaf | Node[Leaf]"] = []
    for element in tree.children:
        if isinstance(element, lark.lark.Tree):  # type: ignore[attr-defined]
            children.append(convert_lark_tree(element))
        elif isinstance(element, lark.lexer.Token):
            children.append(
                Leaf(element.type, element.value, element.line, element.column, element.end_line, element.end_column)
            )
        else:
            raise RuntimeError(f"encountered invalid node in Lark tree: {element!r}")
    return Node(str(tree.data), children)


def from_string(grammar: str, parser: Parser = Parser.EARLEY, start: str = "start", **options: Any) -> Lakai:
    """Create a Lakai parser using the Lark grammar string."""

    return Lakai(_lark.Lark(grammar, parser=parser.name.lower(), start=start, **options))


def from_resource(
    package: str, filename: str, encoding: str, parser: Parser = Parser.EARLEY, start: str = "start", **options: Any
) -> Lakai:
    """Create a Lakai parser using the Lark grammar loaded via :mod:`pkg_resources`."""

    grammar = pkg_resources.resource_string(package, filename).decode(encoding)
    return from_string(grammar, parser=parser, start=start, **options)


def pformat(tree: Node[Leaf], indent: str = "  ", level: int = 0, colored: bool = False) -> str:
    fp = io.StringIO()
    pprint(tree, indent, level, colored, fp)
    return fp.getvalue()


def pprint(
    tree: Node[Leaf], indent: str = "  ", level: int = 0, colored: Optional[bool] = None, fp: Optional[TextIO] = None
) -> None:
    def _colored(s: str, *args: Any, **kwargs: Any) -> str:
        return s

    fp = fp or sys.stdout
    if colored is True or (fp in (sys.stdout, sys.stderr) and fp.isatty() and colored is None):
        try:
            from termcolor import colored as _colored  # type: ignore[no-redef]  # noqa: F811
        except ImportError:
            if colored is True:
                raise

    print(f"{indent * level}{_colored(tree.name, 'magenta')}", file=fp)
    for child in tree.children:
        if isinstance(child, Node):
            pprint(child, indent, level + 1, colored, fp)
        else:
            print(
                f"{indent * (level + 1)}{_colored(child.type, 'green')}:",
                f"{_colored(repr(child.value), 'yellow', attrs=['bold'])}",
                file=fp,
            )
