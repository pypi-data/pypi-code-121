import math

import networkx as nx

def shortest_simple_paths(graph, source, target, weight=None):
    try:
        yield from nx.shortest_simple_paths(graph, source, target, weight)
    except nx.NetworkXNoPath:
        yield []


def _find_singular_simple_hierarchy_path(graph, start, end, optionals=False):
    """
    Assuming the graph contains only edges from top to bottom which are labelled singular and not optional.
    x-[singular]->y "y has 1 x", "x can have many y"
    In this case, we always look for start<-end first otherwise look for end<-start (and reverse the path)
    """
    def filt(u, v):
        edge = graph.edges[u, v]
        return edge['singular'] and (not edge['optional'] if optionals else True)  # this only works if all paths have equal weight otherwise
    g = nx.subgraph_view(graph, filter_edge=filt)
    try:
        path = next(nx.shortest_simple_paths(g, end, start, 'optional'))[::-1]
    except nx.NetworkXNoPath:
        path = next(nx.shortest_simple_paths(g, start, end, 'optional'))
    return path


def find_singular_simple_hierarchy_path(graph, start, end):
    """
    If there is a path without optionals then take it, otherwise we want the fewest optional edges
    """
    return _find_singular_simple_hierarchy_path(graph, start, end, optionals=False)



def _find_path(graph, a, b, force_single):
    singles = nx.subgraph_view(graph, filter_edge=lambda u, v: graph.edges[u, v]['singular'])
    # first try to find a singular path
    single_paths = [i for i in [next(shortest_simple_paths(singles, a, b)), next(shortest_simple_paths(singles, b, a))[::-1]] if i]
    if single_paths:
        return min(single_paths, key=len)
    elif force_single:
        raise nx.NetworkXNoPath('No path found between {} and {}'.format(a, b))
    # then try to find a non-singular path with one direction, either -> or <-
    # we dont want ()->()<-() when it's multiple
    restricted = nx.subgraph_view(graph, filter_edge=lambda u, v: graph.edges[u, v]['actual_number'] > 0 and 'relation' in graph.edges[u, v])
    forward = next(shortest_simple_paths(restricted, a, b, 'actual_number'))
    forward_weight = nx.path_weight(restricted, forward, 'actual_number') or math.inf
    reversed = restricted.reverse()
    backward = next(shortest_simple_paths(reversed, a, b, 'actual_number'))
    backward_weight = nx.path_weight(reversed, backward, 'actual_number') or math.inf
    if not forward and not backward:
        raise nx.NetworkXNoPath('No path found between {} and {}'.format(a, b))
    if backward_weight < forward_weight:
        return backward
    return forward



def find_path(graph, a, b, force_single):
    path = _find_path(graph, a, b, force_single)
    if len(path) == 1:
        return [path[0], path[0]]
    return path