from .tnode import TNode
from typing import Generic

class Edge(Generic[TNode]):
    """Defines an edge between two nodes of a graph."""

    def __init__(self, source: TNode, target: TNode) -> None:
        """Initializes a new instance.

        :param source: The source node of the edge.
        :type source: TNode
        :param target: The target node of the edge.
        :type target: TNode
        """

        super().__init__()
        self.__source: TNode = source
        self.__target: TNode = target

    @property
    def source(self) -> TNode:
        """Gets the source node of the edge.

        :return: The source node of the edge.
        :rtype: TNode
        """

        return self.__source

    @property
    def target(self) -> TNode:
        """Gets the target node of the edge.

        :return: The target node of the edge.
        :rtype: TNode
        """

        return self.__target

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.__source == other.source and self.__target == other.target
