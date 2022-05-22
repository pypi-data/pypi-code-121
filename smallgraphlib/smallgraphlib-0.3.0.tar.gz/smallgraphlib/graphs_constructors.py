import random
from typing import List, Tuple

from smallgraphlib import Graph
from smallgraphlib.graph import (
    _TIKZ_EXPORT_MAX_MULTIPLE_EDGES_SUPPORT,
    _TIKZ_EXPORT_MAX_MULTIPLE_LOOPS_SUPPORT,
    Counter,
    DirectedGraph,
)


def graph(nodes, *edges, directed=False):
    """Factory function to create graphs."""
    cls = DirectedGraph if directed else Graph
    return cls(nodes, *edges)


def complete_graph(n: int):
    """Return complete graph K(n)."""
    nodes = list(range(1, n + 1))
    edges = ((i, j) for i in nodes for j in nodes if i < j)
    return Graph(nodes, *edges)


def complete_bipartite_graph(n: int, m: int):
    """Return complete bipartite graph K(n, m)."""
    return Graph(range(1, m + n + 1), *((i, j) for i in range(1, n + 1) for j in range(n + 1, n + 1 + m)))


def random_graph(
    order: int,
    degree: int,
    *,
    directed=True,
    simple=False,
    tikz_export_supported=True,
    max_multiple_edges: int = None,
    max_multiple_loops: int = None,
):
    """Create a random graph satisfying given constraints.

    Raise a ValueError if contraints can't be satisfied.

    If `simple` is True, ignore remaining keyword arguments.
    Similarly, if `tikz_export_supported` is True, all remaining keyword arguments will be ignored.
    """
    # Test for feasibility: is it possible to satisfy all constraints ?
    if simple:
        max_degree_for_simple_graph = order * (order - 1)
        if not directed:
            max_degree_for_simple_graph //= 2
        if degree > max_degree_for_simple_graph:
            graph_type = "directed" if directed else "undirected"
            raise ValueError(
                f"Degree is at most {max_degree_for_simple_graph} "
                f"for a simple {graph_type} graph of order {order}."
            )
    if simple:
        if max_multiple_edges is not None or max_multiple_loops is not None:
            raise ValueError(
                "Conflicting arguments: `simple` must be set to False, "
                "else `max_multiple_edges` and `max_multiple_loops` will be ignored."
            )
        max_multiple_edges = 1
        max_multiple_loops = 0
    elif tikz_export_supported:
        if max_multiple_edges is not None or max_multiple_loops is not None:
            raise ValueError(
                "Conflicting arguments: `tikz_export_supported` must be set to False, "
                "else `max_multiple_edges` and `max_multiple_loops` will be ignored."
            )
        max_multiple_edges = _TIKZ_EXPORT_MAX_MULTIPLE_EDGES_SUPPORT
        max_multiple_loops = _TIKZ_EXPORT_MAX_MULTIPLE_LOOPS_SUPPORT
    else:
        if max_multiple_edges is None:
            max_multiple_edges = degree
        if max_multiple_loops is None:
            max_multiple_loops = degree

    if directed:
        max_degree = order * (max_multiple_loops + (order - 1) * max_multiple_edges)
    else:
        max_degree = order * max_multiple_loops + (order * (order - 1) * max_multiple_edges) // 2

    if degree > max_degree:
        raise ValueError(f"Degree must not exceed {max_degree} with given contraints.")

    nodes: List[int] = list(range(1, order + 1))
    edges: List[Tuple[int, int]] = []

    # Keep track of remaining edges possibilities, for each (start, end) nodes couple.
    counters = {
        start: counter
        for start in nodes
        if (
            counter := Counter(
                {
                    end: (max_multiple_loops if start == end else max_multiple_edges)
                    for end in nodes
                    if directed or start <= end  # for undirected graph, only keep start <= end
                }
            )
        ).total()
        > 0
    }
    # Keep only nodes which accept edges (all except the last one
    # for undirected simple graph, since start < end).
    starts = list(counters)

    while len(edges) < degree:
        start = random.choice(starts)
        counter = counters[start]
        assert counter.total() > 0, counter
        end = random.choice(list(counter.elements()))
        counter[end] -= 1
        if counter.total() == 0:
            # Don't select anymore this node as start point: we can't add any other edge to it.
            starts.remove(start)
        edges.append((start, end))  # Loop will always end. :)
    return graph(nodes, *edges, directed=directed)
