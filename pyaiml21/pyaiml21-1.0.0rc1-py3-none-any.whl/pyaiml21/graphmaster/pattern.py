"""The class for representing pattern tags."""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Iterable, Tuple, List
if TYPE_CHECKING:
    from pyaiml21.ast import Node
    from pyaiml21.parser import Logger
    from .graphmaster import GraphMaster
    from .node import GMNode


MatchFn = Callable[
    [List[str], int, 'GMNode', 'GraphMaster'],
    Iterable[Tuple['GMNode', int]]
]


@dataclass
class Pattern:
    """
    A collection of data and functions representing a <pattern> node.

    Each `Pattern` has assigned:
        - `priority`: defines the order of pattern matching (the higher
          priority, the sooner it is matched)
        - `is_star`: whether this node represents a node from which
          the result can be obtained by <star> tag
        - `parse`: function that takes a node and validates its syntax
          structure; it is guaranteed that `recognises` returns `True`
        - `recognises`: function to check whether the node has type that
          can be matched with this pattern
        - `advance`: a function that given current node returns the next
          node to store in the graphmaster; it is guaranteed the `recognises`
          returns `True`
        - `match`: function used to match against this pattern node
    """

    priority: float
    """priority of matching, the higher the better"""
    is_star: bool
    """is this a star match?"""
    parse: Callable[[Node, Logger], bool]
    """is current node an instance of this pattern - during parsing"""
    recognises: Callable[[Node], bool]
    """is current node an instance of this pattern - condition for advance"""
    advance: Callable[['GMNode', Node], 'GMNode']
    """after input is recognised, store it and return next node"""
    match: MatchFn
    """Match the next word(s).

    Input: words, position of current word, current node, graphmaster
    Output: iterable of next nodes and number of matched words
    Preconditions: the position never points outside the sequence

    This function is used by the `Pattern` nodes to gradually match the
    sequence of Input Path words. Each returned  tuple represents the next
    node to continue matching and the number of words we have matched from
    the sequence.
    """
