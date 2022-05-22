#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  7 12:24:58 2022

@author: nicolas
"""
import collections
from abc import abstractmethod, ABC
from functools import wraps
from itertools import chain
from math import inf
from typing import (
    Set,
    Union,
    Tuple,
    Dict,
    List,
    Iterable,
    FrozenSet,
    Counter as CounterType,
    Any,
    Protocol,
    TypeVar,
    Generic,
)
import random


_TIKZ_EXPORT_MAX_MULTIPLE_EDGES_SUPPORT = 3
_TIKZ_EXPORT_MAX_MULTIPLE_LOOPS_SUPPORT = 1


class ComparableAndHashable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self, other) -> bool:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...


# Node = TypeVar("Node", bound=typing.Hashable)  # too subtile for Pycharm
Node = TypeVar("Node", bound=ComparableAndHashable)
DirectedEdge = Tuple[Node, Node]
UndirectedEdge = FrozenSet[Node]
Edge = Union[DirectedEdge, UndirectedEdge]
EdgeLike = Union[Edge, Set[Node], Iterable[Node]]

Label = Any
InternalGraphRepresentation = Dict[Node, Dict[Node, Union[int, List[Label]]]]


def cached(f):
    """Decorator used to cache results in `self._cache` dictionary."""

    @wraps(f)
    def cached_f(self=None, *args, **kw):
        key = f.__name__
        try:
            if key in self._cache:
                return self._cache[key]
        except AttributeError:
            self._cache = {}
        result = f(self, *args, **kw)
        self._cache[key] = result
        return result

    return cached_f


def cached_property(f):
    return property(cached(f))


def clear_cache(f):
    """Decorator to indicate that a function must invalidate the cache."""

    @wraps(f)
    def cached_f(self=None, *args, **kw):
        result = f(self, *args, **kw)
        try:
            self._cache.clear()
        except AttributeError:
            self._cache = {}
        return result

    return cached_f


# Subclass UserDict, not dict, to call __setitem__ on initialisation too.
class Counter(collections.UserDict, collections.Counter):  # type: ignore
    """A counter that automatically removes empty keys."""

    def __setitem__(self, key, value):
        if not isinstance(value, int):
            raise ValueError(f"Counter value must be an integer, not {value!r}.")
        super().__setitem__(key, value)
        if self[key] == 0:
            del self[key]
        elif self[key] < 0:
            raise ValueError(f"Counter value can't be negative for key {key!r}.")

    def total(self) -> int:
        return sum(self.values())


class CycleFoundError(AttributeError):
    pass


class AbstractGraph(ABC, Generic[Node]):
    def __init__(
        self,
        nodes: Iterable[Node],
        *edges: EdgeLike,
        sort_nodes: bool = True,
    ):
        """Create a graph of nodes, when nodes may be any hashable objects.

        Edges may be any iterable of two nodes.

        If the graph is directed and the edge is a set {A, B} of two nodes,
        then two edges are added, one from A to B and one from B to A.
        Note that in that case, adding {A} will result in two edges too.
        """
        self._successors: Dict[Node, CounterType[Node]] = {}
        if self.is_directed:
            self._predecessors: Dict[Node, CounterType[Node]] = {}
        else:
            self._predecessors = self._successors
        # Nodes must be added before edges.
        if sort_nodes:
            nodes = sorted(nodes)
        self.add_nodes(*nodes)
        self.add_edges(*edges)

    @classmethod
    def from_string(cls, string: str):
        """DirectedGraph.from_string("A:B,C B:C C") will generate a graph of 3 nodes, A, B and C, with
        edges A->B, A->C and B->C."""
        nodes: List[str] = []
        edges: List[Tuple[str, str]] = []
        for substring in string.split():
            node, *remaining = substring.split(":", 1)
            nodes.append(node.strip())
            if remaining:
                edges.extend((node, successor.strip()) for successor in remaining[0].split(","))
        return cls(nodes, *edges)  # type: ignore

    def _add_node(self, node: Node) -> None:
        self._successors[node] = Counter()
        self._predecessors[node] = Counter()

    @clear_cache
    def add_nodes(self, *new_nodes: Node) -> None:
        for node in new_nodes:
            if node in self.nodes:
                raise RuntimeError(f"Node already present: {node!r}")
            self._add_node(node)

    @clear_cache
    def remove_nodes(self, *nodes: Node) -> None:
        for node in nodes:
            if node not in self.nodes:
                raise ValueError(f"Node {node} not found!")
        for node in nodes:
            node_successors = self._successors.pop(node, ())
            for successor in node_successors:
                self._predecessors.get(successor, {}).pop(node, None)  # type: ignore
            predecessors = self._predecessors.pop(node, ())
            for predecessor in predecessors:
                self._successors.get(predecessor, {}).pop(node, None)  # type: ignore

    @staticmethod
    def _get_edge_extremities(edge: EdgeLike) -> Tuple[Node, Node]:
        nodes = iter(edge)
        start = next(nodes)
        try:
            end = next(nodes)
        except StopIteration:
            end = start
        try:
            next(nodes)
            raise ValueError(f"Too many values for an edge: {edge!r}")
        except StopIteration:
            pass
        return start, end

    def _test_edges(self, *edges: EdgeLike) -> None:
        edges_nodes = set(chain(*edges))
        nodes = set(self.nodes)
        if not edges_nodes.issubset(nodes):
            raise ValueError(f"Nodes not found: {edges_nodes - nodes}")

    @clear_cache
    def add_edges(self, *new_edges: EdgeLike) -> None:
        self._test_edges(*new_edges)
        for edge in new_edges:
            start, end = self._get_edge_extremities(edge)
            self._successors[start][end] += 1
            self._predecessors[end][start] += 1
            if self.is_directed and isinstance(edge, (set, frozenset)):
                # This is a bidirectional edge.
                # Note that bidirectional loops are added twice too.
                self._successors[end][start] += 1
                self._predecessors[start][end] += 1

    @clear_cache
    def remove_edges(self, *edges: EdgeLike) -> None:
        self._test_edges(*edges)

        for edge in edges:
            start, end = self._get_edge_extremities(edge)
            self._successors[start][end] -= 1
            self._predecessors[end][start] -= 1
            # if self.is_directed:
            #     self._successors[end][start] -= 1

    @property
    @abstractmethod
    def is_directed(self) -> bool:
        ...

    @property
    def order(self) -> int:
        return len(self.nodes)

    @property
    def degree(self) -> int:
        return sum(self.node_degree(node) for node in self.nodes) // 2

    # Nodes must be ordered, to generate the matrix, so do *not* return a set.
    @cached_property
    def nodes(self) -> Tuple[Node, ...]:
        return tuple(self._successors)

    @cached_property
    def edges(self) -> Tuple[Edge, ...]:
        edges_count: CounterType[Edge] = Counter()
        for node in self.nodes:
            for successor in self.successors(node):
                edge: Edge = self._edge(node, successor)
                edges_count[edge] += self.count_edges(node, successor)
        if not self.is_directed:
            for key in edges_count:
                edges_count[key] //= 2
        return tuple(edges_count.elements())

    @cached_property
    def has_loop(self) -> bool:
        return any(node in self.successors(node) for node in self.nodes)

    @cached_property
    def has_multiple_edges(self) -> bool:
        return len(self.edges) != len(set(self.edges))

    @cached_property
    def is_simple(self) -> bool:
        return not (self.has_loop or self.has_multiple_edges)

    @cached_property
    def is_complete(self) -> bool:
        return self.is_simple and all(
            self.are_adjacents(i, j) for i in self.nodes for j in self.nodes if i != j
        )

    def _test_connection_from_node(self, node: Node) -> bool:
        """Test if every other node can be accessed from node `node`"""
        if self.order <= 1:
            return True
        connected_nodes = set()
        border = {node}
        while border:
            node = border.pop()
            connected_nodes.add(node)
            border |= self.successors(node) - connected_nodes
        return len(connected_nodes) == self.order

    @property
    @abstractmethod
    def is_connected(self):
        ...

    def count_edges(self, node1: Node, node2: Node):
        """Count the number of edges from node1 to node2. Note that undirected loops are counted twice."""
        return self._successors[node1][node2]

    def weight(self, node1, node2) -> float:
        return 1

    def node_degree(self, node: Node) -> int:
        if self.is_directed:
            return self.in_degree(node) + self.out_degree(node)
        return self.out_degree(node)

    def in_degree(self, node: Node) -> int:
        return sum(self._predecessors[node].values())

    def out_degree(self, node: Node) -> int:
        return sum(self._successors[node].values())

    def successors(self, node: Node) -> Set[Node]:
        return set(self._successors[node])

    def predecessors(self, node: Node) -> Set[Node]:
        return set(self._predecessors[node])

    def copy(self):
        return self.__class__(self.nodes, *self.edges)

    @cached_property
    def adjacency_matrix(self) -> Tuple[Tuple[int, ...], ...]:
        return tuple(tuple(self.count_edges(start, end) for end in self.nodes) for start in self.nodes)

    @abstractmethod
    def are_adjacents(self, node1: Node, node2: Node) -> bool:
        ...

    @property
    @abstractmethod
    def is_eulerian(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_semi_eulerian(self) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def _edge(node1, node2) -> Edge:
        ...

    def as_tikz(self, shuffle_nodes=False) -> str:
        lines: List[str] = [
            r"\begin{tikzpicture}["
            r"every node/.style = {draw, circle,font={\scriptsize},inner sep=2},"
            "directed/.style = {-{Stealth[scale=1.1]}},"
            "reversed/.style = {{Stealth[scale=1.1]}-},"
            "undirected/.style = {},"
            "]"
        ]
        theta = 360 / self.order
        angles = {}
        nodes = list(self.nodes)
        if shuffle_nodes:
            random.shuffle(nodes)
        for i, node in enumerate(nodes):
            angle = angles[node] = i * theta
            lines.append(rf"\node ({node}) at ({angle}:1cm) {{${node}$}};")
        nodes_pairs = {frozenset((node1, node2)) for node1 in nodes for node2 in nodes}
        pair: FrozenSet[Node]
        for pair in nodes_pairs:
            style = "directed" if self.is_directed else "undirected"
            if len(pair) == 1:
                (node,) = pair
                n: int = self.count_edges(node, node)
                if not self.is_directed:
                    assert n % 2 == 0, n
                    n //= 2
                if n > _TIKZ_EXPORT_MAX_MULTIPLE_LOOPS_SUPPORT:
                    raise NotImplementedError(n)
                if n == 1:
                    lines.append(
                        rf"\draw[{style}] ({node}) to "
                        f"[out={angles[node] - 45},in={angles[node] + 45},looseness=5] ({node});"
                    )
            else:
                node1, node2 = pair
                if self.is_directed:
                    n1 = self.count_edges(node1, node2)
                    n2 = self.count_edges(node2, node1)
                    n = n1 + n2
                    styles = n1 * ["directed"] + n2 * ["reversed"]
                else:
                    n = self.count_edges(node1, node2)
                    styles = n * ["undirected"]
                if n == 0:
                    curves = []
                elif n == 1:
                    curves = [""]
                elif n == 2:
                    curves = ["bend left", "bend right"]
                elif n == 3:
                    curves = ["bend left", "", "bend right"]
                else:
                    assert n > _TIKZ_EXPORT_MAX_MULTIPLE_EDGES_SUPPORT
                    raise NotImplementedError(n)
                for style, curve in zip(styles, curves):
                    lines.append(rf"\draw[{style}] ({node1}) to[{curve}] ({node2});")

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    def _dijkstra(self, start: Node, end: Node = None) -> Tuple[Dict[Node, float], Dict[Node, List[Node]]]:
        """Implementation of Dijkstra Algorithm."""
        if start not in self.nodes:
            raise ValueError(f"Unknown node {start!r}.")
        if end is not None and end not in self.nodes:
            raise ValueError(f"Unknown node {end!r}.")
        lengths: Dict[Node, float] = {node: (0 if node == start else inf) for node in self.nodes}
        last_step: Dict[Node, List[Node]] = {node: [] for node in self.nodes}
        never_selected_nodes = set(self.nodes)
        selected_node = start
        while selected_node != end and len(never_selected_nodes) > 1:
            never_selected_nodes.remove(selected_node)
            for successor in self.successors(selected_node) & never_selected_nodes:
                weight = self.weight(selected_node, successor)
                if weight < 0:
                    raise ValueError("Can't find shortest paths with negative weights.")
                new_length = lengths[selected_node] + weight
                if new_length < lengths[successor]:
                    lengths[successor] = new_length
                    last_step[successor] = [selected_node]
                elif new_length == lengths[successor]:
                    last_step[successor].append(selected_node)
            selected_node = min(never_selected_nodes, key=(lambda node_: lengths[node_]))
        return lengths, last_step

    def distance(self, start: Node, end: Node) -> float:
        """Implementation of Dijkstra Algorithm."""
        lengths, last_step = self._dijkstra(start, end)
        return lengths[end]

    @cached_property
    def diameter(self) -> float:
        return max(self.distance(node1, node2) for node1 in self.nodes for node2 in self.nodes)

    def shortest_paths(self, start: Node, end: Node) -> Tuple[float, List[List[Node]]]:
        """Implementation of Dijkstra Algorithm."""
        lengths, last_step = self._dijkstra(start, end)

        def generate_paths(path: List[Node]) -> List[List[Node]]:
            if path[0] == start:
                return [path]
            paths = []
            for predecessor in last_step[path[0]]:
                paths.extend(generate_paths([predecessor] + path))
            return paths

        return lengths[end], generate_paths([end])


class Graph(AbstractGraph):
    """A graph with undirected edges.

    >>> G = Graph((1, 2, 3), {1, 3}, {1, 2}, {2, 1}, {1})
    """

    def __repr__(self):
        edges = (repr(set(edge)) for edge in self.edges)
        return f"Graph({tuple(self.nodes)!r}, {', '.join(edges)})"

    @property
    def is_directed(self):
        return False

    @staticmethod
    def _edge(node1, node2) -> UndirectedEdge:
        return frozenset((node1, node2))

    def _count_odd_degrees(self):
        return sum(self.node_degree(node) % 2 for node in self.nodes)

    @cached_property
    def is_eulerian(self):
        return self._count_odd_degrees() == 0

    @cached_property
    def is_semi_eulerian(self):
        return self._count_odd_degrees() == 2

    @cached_property
    def is_connected(self):
        return self._test_connection_from_node(next(iter(self.nodes)))

    @cached_property
    def greedy_coloring(self) -> Dict[Node, int]:
        coloring: Dict[Node, int] = {}
        # Sort nodes by reversed degree, then alphabetically
        nodes = sorted(self.nodes, key=(lambda _node: (-self.node_degree(_node), _node)))
        for node in nodes:
            color_num = 0
            while any(coloring.get(adjacent) == color_num for adjacent in self.successors(node)):
                color_num += 1
            coloring[node] = color_num
        return coloring

    def are_adjacents(self, node1: Node, node2: Node) -> bool:
        return node2 in self.successors(node1)

    @property
    def weighted_graph(self):
        from smallgraphlib import WeightedGraph

        def weighted_edge(edge):
            start, end = self._get_edge_extremities(edge)
            return start, end, 1

        return WeightedGraph(self.nodes, *(weighted_edge(edge) for edge in self.edges))

    def is_subgraph_stable(self, *nodes: Node) -> bool:
        return not any(self.are_adjacents(node1, node2) for node1 in nodes for node2 in nodes)

    @cached_property
    def is_complete_bipartite(self) -> bool:
        nodes_group = self.successors(self.nodes[0])
        other_group = set(self.nodes) - nodes_group
        if not self.is_subgraph_stable(*nodes_group):
            return False
        if not self.is_subgraph_stable(*other_group):
            return False
        return all(self.are_adjacents(node1, node2) for node1 in nodes_group for node2 in other_group)


class DirectedGraph(AbstractGraph):
    """A graph with directed edges.

    >>> G = DirectedGraph((1, 2, 3), (1, 3), (1, 2), (2, 1), (1, 1))
    """

    def __repr__(self):
        edges = (repr(edge) for edge in self.edges)
        return f"DirectedGraph({tuple(self.nodes)!r}, {', '.join(edges)})"

    @property
    def is_directed(self):
        return True

    @staticmethod
    def _edge(node1, node2) -> DirectedEdge:
        return node1, node2

    @cached_property
    def is_eulerian(self):
        return all(self.out_degree(node) == self.in_degree(node) for node in self.nodes)

    @cached_property
    def is_semi_eulerian(self):
        start_found = end_found = False
        for node in self.nodes:
            out_degree = self.out_degree(node)
            in_degree = self.in_degree(node)
            if out_degree == in_degree + 1 and not start_found:
                start_found = True
            elif out_degree == in_degree - 1 and not end_found:
                end_found = True
            elif out_degree != in_degree:
                return False
        return start_found and end_found

    @cached_property
    def levels(self) -> Tuple[FrozenSet[Node], ...]:
        graph = self.copy()
        levels: List[FrozenSet] = []
        while True:
            level = set()
            for node in graph.nodes:
                if graph.out_degree(node) == 0:  # is node a sink ?
                    level.add(node)
            if len(level) == 0:
                break
            graph.remove_nodes(*level)
            levels.append(frozenset(level))
        if graph.order != 0:
            raise CycleFoundError("Can't split the graph into levels, since it has a closed path.")
        return tuple(levels)

    @cached_property
    def kernel(self) -> FrozenSet[Node]:
        graph = self.copy()
        kernel = set()
        while True:
            nodes_to_remove = set()
            for node in graph.nodes:
                if graph.out_degree(node) == 0:  # is node a sink ?
                    kernel.add(node)
                    nodes_to_remove.add(node)
                    nodes_to_remove |= self.predecessors(node)

            if len(nodes_to_remove) == 0:
                break
            graph.remove_nodes(*nodes_to_remove)
        if graph.order != 0:
            raise CycleFoundError("Can't compute the graph's kernel, since it has a closed path.")
        return frozenset(kernel)

    @cached_property
    def has_cycle(self) -> bool:
        return not hasattr(self, "levels")

    @property
    def reversed_graph(self):
        return DirectedGraph(self.nodes, *(edge[::-1] for edge in self.edges))

    @property
    def undirected_graph(self):
        return Graph(self.nodes, *self.edges)

    @property
    def weighted_graph(self):
        from smallgraphlib import WeightedDirectedGraph

        return WeightedDirectedGraph(self.nodes, *(edge + (1,) for edge in self.edges))

    @cached_property
    def is_strongly_connected(self):
        node = next(iter(self.nodes))
        return self._test_connection_from_node(node) and self.reversed_graph._test_connection_from_node(node)

    @cached_property
    def is_connected(self):
        return self.undirected_graph.is_connected

    def are_adjacents(self, node1: Node, node2: Node) -> bool:
        return node2 in (self.successors(node1) | self.predecessors(node1))
