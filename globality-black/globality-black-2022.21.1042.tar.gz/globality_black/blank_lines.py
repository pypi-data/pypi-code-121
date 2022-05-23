"""
Module to cover/uncover specific blank lines in pre/post processor
 so that black does not remove them

The blank lines we want to cover are those added explicitly by the developer to improve
readability, e.g. blank lines below:

graph.use(
    "logging",

    "space",

    # Sagemaker basics
    "sagemaker",

    # This line causes ...
    "load_active_bundle_and_dependencies",
)
"""
import re

from globality_black.common import apply_function_to_tree_prefixes
from globality_black.constants import BLANK_LINE_TOKEN


def cover_blank_lines(module, root):
    apply_function_to_tree_prefixes(module, root, add_token_if_line_to_keep)


def add_token_if_line_to_keep(prefix):
    # Add a token when two or more new lines (optionally with spaces in them)
    # We use " " and not "\s" since the latter denotes any whitespace character, included \r,\n, etc
    return re.sub(
        r"(?:\n *)+\n( +)",
        fr"\n\1# {BLANK_LINE_TOKEN}\n\1",
        prefix,
    )


def uncover_blank_lines(module, root):
    apply_function_to_tree_prefixes(
        module,
        root,
        remove_token_from_covered_line,
    )


def remove_token_from_covered_line(prefix):
    # Note that black will add spaces before the token

    return re.sub(
        fr"\n +# {BLANK_LINE_TOKEN}\n",
        r"\n\n",
        prefix,
    )
