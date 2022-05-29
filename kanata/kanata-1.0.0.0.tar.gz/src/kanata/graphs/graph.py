from .edge import Edge
from .tnode import TNode
from .exceptions import DuplicateEdgeException, DuplicateNodeException
from typing import Generic, List, Set, Tuple

class Graph(Generic[TNode]):
    """A basic, non-directed graph that consists of nodes and edges between them."""

    def __init__(self, allow_parallel_edges: bool = False) -> None:
        """Initializes a new instance.

        :param allow_parallel_edges: Whether multiple edges between the same two nodes are allowed, defaults to False.
        :type allow_parallel_edges: bool, optional
        """

        self.__allow_parallel_edges: bool = allow_parallel_edges
        self.__nodes: Set[TNode] = set()
        self.__edges: List[Edge[TNode]] = []

    @property
    def allow_parallel_edges(self) -> bool:
        """Gets whether multiple edges between the same two nodes are allowed.

        :return: Whether multiple edges between the same two nodes are allowed.
        :rtype: bool
        """

        return self.__allow_parallel_edges

    @property
    def nodes(self) -> Set[TNode]:
        """Gets the set of nodes this graphs consist of.

        :return: The set of nodes this graphs consist of.
        :rtype: Set[TNode]
        """

        return self.__nodes.copy()

    @property
    def edges(self) -> Tuple[Edge[TNode], ...]:
        """Gets the collection of edges between the nodes.

        :return: The collection of edges between the nodes.
        :rtype: Tuple[Edge[TNode], ...]
        """

        return tuple(self.__edges)

    def add_node(self, node: TNode) -> None:
        """Adds a node that hasn't been added to the graph yet.

        :param node: The node to be added.
        :type node: TNode
        :raises DuplicateNodeException: Raised when the node to be added is already part of the graph.
        """

        if node in self.__nodes:
            raise DuplicateNodeException(node, "The given node is already part of the graph.")
        self.__nodes.add(node)

    def try_add_node(self, node: TNode) -> bool:
        """Adds a new node to the graphi if it hasn't been added yet.

        :param node: The node to be added.
        :type node: TNode
        :return: True, if the node has been added; false, if it's already present.
        :rtype: bool
        """

        if node in self.__nodes:
            return False
        self.__nodes.add(node)
        return True

    def add_edge(self, source: TNode, target: TNode) -> None:
        """Adds an edge that may or may have not been added yet to the graph.

        :param source: The source node of the edge.
        :type source: TNode
        :param target: The target node of the edge.
        :type target: TNode
        :raises DuplicateEdgeException: Raised when parallel edges aren't allowed and an identical edge is already added.
        """

        if not self.try_add_edge(source, target):
            raise DuplicateEdgeException(source, target)

    def try_add_edge(self, source: TNode, target: TNode) -> bool:
        """Adds an edge to the graph between the specified nodes if a) such an edge doesn't exist yet, or b) parallel edges are allowed.

        :param source: The source node of the edge.
        :type source: TNode
        :param target: The target node of the edge.
        :type target: TNode
        :return: True, if the edge has been added; false, if it's already present.
        :rtype: bool
        """

        new_edge = Edge(source, target)
        if self.__allow_parallel_edges:
            self.__edges.append(new_edge)
            return True

        for edge in self.__edges:
            if self._is_same_edge(edge, new_edge):
                return False

        self.__edges.append(new_edge)
        return True

    def _is_same_edge(self, existing_edge: Edge, new_edge: Edge) -> bool:
        """Determines whether two edges are equal.

        Override this method in sub-classes to determine if two edges are equal. By default,
        two edges are equal if and only if their sources and targets are equal in any combination.

        :param existing_edge: The already existing edge.
        :type existing_edge: Edge
        :param new_edge: The new edge.
        :type new_edge: Edge
        :return: True, if the two edges are equal.
        :rtype: bool
        """

        return (
            (existing_edge.source == new_edge.source and existing_edge.target == new_edge.target)
            or (existing_edge.source == new_edge.target and existing_edge.target == new_edge.source)
        )

    def __contains__(self, item: object) -> bool:
        return item in self.__nodes
