import networkx as nx

def shortest_simple_paths(graph, source, target):
    try:
        yield from nx.shortest_simple_paths(graph, source, target)
    except nx.NetworkXNoPath:
        yield []


def find_singular_simple_hierarchy_path(graph, start, end):
    """
    Assuming the graph contains only edges from top to bottom which are labelled singular and not optional.
    x-[singular]->y "y has 1 x", "x can have many y"
    In this case, we always look for start<-end first otherwise look for end<-start (and reverse the path)
    """
    def filt(u, v):
        edge = graph.edges[u, v]
        return edge['singular'] and 'relation' in edge and not edge['optional']
    g = nx.subgraph_view(graph, filter_edge=filt)
    try:
        return next(nx.shortest_simple_paths(g, end, start))
    except nx.NetworkXNoPath:
        return next(nx.shortest_simple_paths(g, start, end))




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
    # restricted = nx.subgraph_view(graph, filter_edge=lambda u, v: 'relation' in graph.edges[u, v] or graph.edges[u, v]['singular'])
    restricted = nx.subgraph_view(graph, filter_edge=lambda u, v: 'relation' in graph.edges[u, v])
    paths = [i for i in [next(shortest_simple_paths(restricted, a, b)), next(shortest_simple_paths(restricted, b, a))[::-1]] if i]
    if paths:
        return min(paths, key=len)
    raise nx.NetworkXNoPath('No path found between {} and {}'.format(a, b))

def find_path(graph, a, b, force_single):
    path = _find_path(graph, a, b, force_single)
    if len(path) == 1:
        return [path[0], path[0]]
    return path