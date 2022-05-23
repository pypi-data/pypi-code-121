"""
Module to cover/uncover specific lines in dotted chains, to be used by pre/post processor
 so that black does not merge them together

Examples of dotted chains:

batch = (
    batch
    .sample(frac=self.sample_fraction, random_state=88)
    .reset_index(drop=True)
)

LABELS = set(
    df[df.labels.apply(len) > 0]
    .flag.apply(curate)
    .apply(normalize)
    .unique()
)

We want to keep these as they are. To do so, we will:
 - Add a line with comment with the DOTTED_CHAIN_TOKEN before each line starting with a "."
 (within this context)
 - Remove these extra lines afterwards

"""
import re

from parso.python.tree import PythonNode

from globality_black.common import apply_function_to_tree_prefixes
from globality_black.constants import DOTTED_CHAIN_TOKEN, TAB_CHAR_SIZE


def cover_dotted_chain_if_needed(candidate: PythonNode):
    """
    Check if it is a dotted chain and if so, cover it
    module: contains all python code in this file
    candidate: candidate element to be a dotted chain
    (one of the types in DOTTED_CHAIN_TYPES)
    """
    if is_dotted_chain(candidate):
        cover_dotted_chain(candidate)


def is_dotted_chain(atom_expr: PythonNode) -> bool:
    """
    Assert whether the given atom_expr is a dotted chain

    Examples:

    batch(a)(b)
    .sample(
        frac=param1,
        rs=param2,
    )
    .reset_index(drop1=True)(drop2=True)
    .reset_index(drop=True).reset_index(drop=True)
    --> True

    batch
    (batch)
    --> False

    batch,
    batch,
    --> False

    batch
    .batch
    --> True

    batch
    .batch(
        x=4,
    )
    --> True

    """
    children = atom_expr.children
    new_line_and_indent_regex = rf"\n(?: {{{TAB_CHAR_SIZE}}})+"

    # first node should start with a \n (a new line) + tabs (space characters, multiple of 4)
    prefix_child1 = children[0].get_first_leaf().prefix
    if not re.match(new_line_and_indent_regex, prefix_child1):
        return False

    # more than one child needed to be a dotted chain
    if len(children) < 2:
        return False

    # all children after the first one (which starts with \n + indent) should start with a dot
    # otherwise it's not a dotted chain
    for child in children[1:]:
        code = child.get_code()
        if re.match(new_line_and_indent_regex, code):
            if not code.strip().startswith("."):
                return False

    return True


def cover_dotted_chain(candidate):
    """
    We cannot use `apply_function_to_tree_prefixes` (or not easily) as not all lines in the dotted
    chain are to be modified, only those starting with "." (which is not in the prefix)
    """
    for node in candidate.children[1:]:
        if node.get_code().strip().startswith("."):
            prefix = node.get_first_leaf().prefix
            node.get_first_leaf().prefix = get_new_prefix(prefix)


def get_new_prefix(prefix):
    # Add a token to avoid line merging

    return re.sub(
        r"\n( +)",
        fr"\n\1# {DOTTED_CHAIN_TOKEN}\n\1",
        prefix,
    )


def uncover_dotted_chain(module, root):
    """
    In this case we can apply the function to all lines

    """
    apply_function_to_tree_prefixes(
        module,
        root,
        remove_token_from_covered_dotted_chain_line,
    )


def remove_token_from_covered_dotted_chain_line(prefix):
    # Remove extra lines with DC_TOKEN" added in pre-processing

    return re.sub(
        fr"\n +# {DOTTED_CHAIN_TOKEN}",
        r"",
        prefix,
    )
