"""
- Authors: Peter Mawhorter
- Consulted:
- Date: 2022-4-15
- Purpose: Code for visualizing decision graphs and explorations.

Defines functions for graph layout and drawing for
`exploration.core.DecisionGraph` objects, and for visualizing
`Exploration` objects as an animation or sequence of `DecisionGraph`
images. Since the focal example is Metroidvania games, we use a
square-tiles-based map system as the basis for layout. This will not work
well for non-planar graphs.

TODO: Anchor-free localization implementation?
"""

from typing import Dict, Optional, Tuple

from . import core

BlockPosition = Tuple[int, int, int]
"""
A type alias: block positions indicate the x/y coordinates of the
north-west corner of a node, as well as its side length in grid units
(all nodes are assumed to be square).
"""

BlockLayout = Dict[core.Decision, BlockPosition]
"""
A type alias: block layouts map each decision in a particular graph to a
block position which indicates both position and size in a unit grid.
"""


def roomSize(connections: int) -> int:
    """
    For a room with the given number of connections, returns the side
    length of the smallest square which can accommodate that many
    connections. Note that outgoing/incoming reciprocal pairs to/from a
    single destination should only count as one connection, because they
    don't need more than one space on the room perimeter. Even with zero
    connections, we still return 1 as the room size.
    """
    if connections == 0:
        return 1
    return 1 + (connections - 1) // 4


def expandBlocks(layout: BlockLayout) -> None:
    """
    Modifies the given block layout by adding extra space between each
    positioned node: it triples the coordinates of each node, and then
    shifts them south and east by 1 unit each, by maintaining the nodes
    at their original sizes, 
    """


def blockLayoutFor(region: core.DecisionGraph) -> BlockLayout:
    """
    Computes a unit-grid position and size for each room in an
    `exploration.core.DecisionGraph`, laying out the rooms as
    non-overlapping square blocks. In many cases, connections will be
    stretched across empty space, but no explicit space is reserved for
    connections.
    """
