"""Nodes used in the graphmaster."""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


def _make_node_dict():
    return defaultdict(GMNode)


@dataclass
class GMNode:
    """
    Represents a node in the graphmaster used for storing pattern paths.

    The only usable fields are ``obj`` - for storing whatever should be
    retrieved for the pattern path if this is its last node, and ``children`` -
    a mapping from string to other node.
    """

    obj: Optional[Any] = None  # stored object
    children: Dict[str, "GMNode"] = field(default_factory=_make_node_dict)
