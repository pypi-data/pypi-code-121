"""
Module to cover/uncover size 1 tuples when exploded, to be used by pre/post processor
 so that black does not merge them together

# TODO: remove this once/if https://github.com/psf/black/issues/1139#issuecomment-951014094 solved

See examples in the test cases of tuples_input and tuple_output

"""
import re

from parso.python.tree import PythonNode

from globality_black.common import apply_function_to_tree_prefixes
from globality_black.constants import TUPLE_TOKEN


def cover_tuple_if_needed(candidate: PythonNode):
    """
    Check if it is a tuple to cover if so, cover it
    module: contains all python code in this file
    candidate: candidate element to be a tuple to cover
    (one of the types in TUPLE_TYPES)
    """
    if is_size_one_exploded_tuple(candidate):
        cover_tuple(candidate)


def is_size_one_exploded_tuple(atom: PythonNode) -> bool:
    """
    Assert whether the given atom is a tuple to cover

    """
    # children must be 3  ["(", "item", ")"] and the item must end with a comma (to be a tuple)
    return (
        len(atom.children) == 3
        and atom.children[0] == "("
        and atom.children[1].get_code().endswith(",")
    )


def cover_tuple(candidate):
    """
    Just modify the prefix of the first child, which is the one element in this tuple
    """
    node = candidate.children[1]
    prefix = node.get_first_leaf().prefix
    node.get_first_leaf().prefix = get_new_prefix(prefix)


def get_new_prefix(prefix):
    """Add a token to avoid line merging"""

    return re.sub(
        r"\n( +)",
        fr"\n\1# {TUPLE_TOKEN}\n\1",
        prefix,
    )


def uncover_tuple(module, root):
    """In this case we can apply the function to all lines"""
    apply_function_to_tree_prefixes(
        module,
        root,
        remove_token_from_covered_tuple,
    )


def remove_token_from_covered_tuple(prefix):
    """Remove extra lines with TUPLE_TOKEN added in pre-processing"""

    return re.sub(
        fr"\n +# {TUPLE_TOKEN}",
        r"",
        prefix,
    )
