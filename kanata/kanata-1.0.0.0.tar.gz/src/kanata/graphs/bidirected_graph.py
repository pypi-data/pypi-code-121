from .edge import Edge
from .graph import Graph
from .tnode import TNode
from ..exceptions import ArgumentException
from typing import Generator

class BidirectedGraph(Graph[TNode]):
    """A type of graph whose edges specify a direction between nodes."""

    def __init__(self) -> None:
        super().__init__()

    def get_out_edges(self, node: TNode) -> Generator[Edge[TNode], None, None]:
        """Gets the edges that point outward from the specified node.

        :param node: The node for which to get the out-edges.
        :type node: TNode
        :raises ArgumentException: Raised when the specified node is not in the graph.
        :yield: The edges that point outward from the specified node.
        :rtype: Generator[Edge[TNode], None, None]
        """

        if not node in self:
            raise ArgumentException("node", node, "The specified node is not in the graph.")

        for edge in self.edges:
            if edge.source == node:
                yield edge

    def _is_same_edge(self, existing_edge: Edge, new_edge: Edge) -> bool:
        return existing_edge == new_edge
