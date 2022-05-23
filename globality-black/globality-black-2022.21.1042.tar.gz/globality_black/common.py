import re
from typing import List, Optional

from parso.python.tree import Module

from globality_black.constants import (
    MAX_CHARACTERS_TO_FIND_INDENTATION_PARENT,
    TYPES_TO_CHECK_FMT_ON_OFF,
)


class SyntaxTreeVisitor:
    def __init__(
        self,
        module: Module,
        types_to_find: Optional[List[str]] = None,
    ):
        self.module = module
        self.types_to_find = types_to_find
        self.fmt_off = False

    def __call__(self, node):

        self.set_fmt_on_off_according_to_prefix(node)
        if self.types_to_find is None or node.type in self.types_to_find and not self.fmt_off:
            yield node

        if hasattr(node, "children"):
            for child in node.children:
                self.set_fmt_on_off_according_to_prefix(child)
                if not self.fmt_off:
                    yield from self(child)

    def set_fmt_on_off_according_to_prefix(self, node):
        """
        We check for fmt_on_off only for some specific types, otherwise no-op. This saves time, so
        we don't need to find the prefix for every single node in the parse tree
        """

        if not any(name in node.type for name in TYPES_TO_CHECK_FMT_ON_OFF):
            return
        prefix = node.get_first_leaf().prefix

        if "fmt: off" in prefix:
            self.fmt_off = True

        if "fmt: on" in prefix:
            self.fmt_off = False


def apply_function_to_tree_prefixes(module, root, function):
    visitor = SyntaxTreeVisitor(module)

    for node in visitor(root):
        prefix = node.get_first_leaf().prefix
        node.get_first_leaf().prefix = function(prefix)


def find_indentation_parent_prefix(element):
    """
    Find prefix for the indentation parent by going to the parent's line and getting the indent
    for the first element in the line, i.e. the node we have to align this element with

    Examples:

          x = foo(arg1="marc",) --> indentation parent for arg1 is x (his grand-grand-parent)
          foo(arg1="marc",) --> indentation parent for arg1 is foo (his grand-parent)

    """

    parent = element.parent
    module = element.get_root_node()

    line_start_pos = (parent.start_pos[0], 0)
    leaf = module.get_leaf_for_position(line_start_pos, include_prefixes=True)

    # we move the "pointer" to position 0 of this line and check if the leaf.type is not a newline
    # otherwise we keep moving the pointer until we find something, and that gives as the
    # indentation sized we're looking for
    while leaf.type == "newline":
        leaf = module.get_leaf_for_position(line_start_pos, include_prefixes=True)
        line_start_pos = (line_start_pos[0], line_start_pos[1] + 1)

        if line_start_pos[1] > MAX_CHARACTERS_TO_FIND_INDENTATION_PARENT:
            raise ValueError(
                "Warning: no leaf found in this line after "
                f"{MAX_CHARACTERS_TO_FIND_INDENTATION_PARENT} characters. "
                f"Looking for parent for leaf:\n{leaf.get_code()}"
            )

    return leaf.prefix


def get_indent_from_prefix(prefix):
    """
    Each element in parso has a prefix. We want to get the indent from the parent, so we can
    construct the prefix for the modified elements.

    Example:

         def foo(
            arg1="marc", arg2=" at ", arg3="globality",
        ):
            return arg1 + arg2 + arg3

    arg1 has prefix "\n    ". Here we get the "    ".
    """

    if prefix:
        try:
            return re.search("( *)$", prefix).group(0)
        except Exception:
            raise ValueError(f"Could not get indent from prefix {prefix}")
    else:
        return prefix
