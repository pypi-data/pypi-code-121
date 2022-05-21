from pyaiml21.ast import Node, Category
from .logger import Logger
from typing import Mapping, Callable


TagSyntaxCheckerFn = Callable[[Node, Logger], None]
"""take node and logger and report any syntax warnings/errors"""
SyntaxCheckers = Mapping[str, TagSyntaxCheckerFn]
"""mapping from node tag to function to check its syntax"""


class Walker:
    """
    Functions to recursively check the syntax of AIML elements.

    The tree traversal is done in pre-order so that nodes can modify their
    descendants and the syntax check can be done on them too.
    """

    @staticmethod
    def walk(category: Category, logger: Logger, checkers: SyntaxCheckers):
        """Check the syntax of <template> element using `checkers`."""
        return Walker._walk(category.template, logger, checkers)

    @staticmethod
    def _walk(root: Node, logger: Logger, checkers: SyntaxCheckers):
        if root.is_text_node:
            return  # all text nodes have apriori correct format
        assert root.tag is not None
        if root.tag in checkers:
            checkers[root.tag](root, logger)
        else:
            # skipping through the tag, leaving it as it is
            logger.weak_warning(root, "Unknown tag")
        for k, v in root.attributes.items():
            Walker._walk(v, logger, checkers)
        for child in root.children:
            Walker._walk(child, logger, checkers)
