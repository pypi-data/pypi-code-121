from functools import lru_cache
from typing import List, Tuple

import graphviz
import networkx as nx
from networkx.classes.graphviews import generic_graph_view
from networkx.drawing.nx_pydot import to_pydot


class HashedDiGraph(nx.DiGraph):
    hash_edge_attr = 'type'
    hash_node_attr = 'i'

    @property
    def name(self) -> str:
        return nx.weisfeiler_lehman_graph_hash(self, edge_attr=self.hash_edge_attr, node_attr=self.hash_node_attr)

    @name.setter
    def name(self, s):
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.name)

    def add_node(self, node_for_adding, **attr):
        """add_node but return existing node if it is matched, ignoring attributes"""
        if node_for_adding in self.nodes:
            return node_for_adding
        return super().add_node(node_for_adding, **attr)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """add_edge but return existing node if it is matched"""
        if (u_of_edge, v_of_edge) in self.edges:
            if self.edges[(u_of_edge, v_of_edge)] == attr:
                return (u_of_edge, v_of_edge)
        super().add_edge(u_of_edge, v_of_edge, **attr)


def plot_graph(graph, highlight_nodes=None, highlight_edges=None):
    highlight_nodes = [] if highlight_nodes is None else highlight_nodes
    highlight_edges = [] if highlight_edges is None else highlight_edges
    g = nx.DiGraph()
    for n in graph.nodes:
        g.add_node(n)
        if n in highlight_nodes:
            g.nodes[n]['style'] = 'filled'
    for e in graph.edges():
        try:
            label = e['statement'].make_cypher(graph.nodes)
        except:
            label = ''
        g.add_edge(*e, **graph.edges[e], label=label)
        if e in highlight_edges:
            g.edges[e]['arrowsize'] = 2
    nx.relabel_nodes(g, {n: f"{d['i']}\n{d['label']}" for n, d in graph.nodes(data=True)}, copy=False)
    return graphviz.Source(to_pydot(g).to_string())


def make_node(graph: HashedDiGraph, parent, type: str, statement: 'Statement', single, **edge_data):
    i = graph.number_of_nodes()
    try:
        label = str(statement.output_variables[0])
    except (IndexError, AttributeError):
        label = 'node'
    node = i
    for a, b, d in graph.out_edges(parent, data=True):
        if d.get('statement', None) == statement:
            return b  # node is already there so return it
    graph.add_node(node, label=label, i=i, variables=[])
    if parent is not None:
        graph.add_edge(parent, node, type=type, statement=statement, single=single, **edge_data)
    if statement is not None:
        statement.edge = (parent, node)
    return node


def add_start(graph: HashedDiGraph, name):
    return make_node(graph, None, name, None, False)


def add_traversal(graph: HashedDiGraph, parent, statement, single=False, unwound=None):
    if unwound is not None:
        parent, deps = unwound, [parent]
    else:
        parent, deps = parent, []
    n = make_node(graph, parent, 'traversal', statement, single)
    for d in deps:
        graph.add_edge(d, n, type='dep', style='dotted')
    return n


def add_filter(graph: HashedDiGraph, parent, dependencies, statement):
    n = make_node(graph, parent, 'filter', statement, False)
    for d in dependencies:
        graph.add_edge(d, n, type='dep', style='dotted')
    return n


def add_aggregation(graph: HashedDiGraph, parent, wrt, statement, type='aggr', single=False):
    n = make_node(graph, parent, type, statement, single)
    graph.add_edge(n, wrt, type='wrt', style='dashed')
    return n


def add_operation(graph: HashedDiGraph, parent, dependencies, statement):
    n = make_node(graph, parent, 'operation', statement, True)
    for d in dependencies:
        graph.add_edge(d, n, type='dep', style='dotted')
    return n


def add_return(graph: HashedDiGraph, index, columns, statement):
    n = make_node(graph, index, 'return', statement, True)
    for d in columns:
        graph.add_edge(d, n, type='dep', style='dotted')
    return n


def add_unwind(graph: HashedDiGraph, parent, statement):
    return make_node(graph, parent, 'traversal', statement, single=False)


def subgraph_view(graph: HashedDiGraph, excluded_edge_type=None, only_edge_type=None,
                  only_nodes: List = None, excluded_nodes: List = None,
                  only_edges: List[Tuple] = None, excluded_edges: List[Tuple] = None,
                  path_to = None,
                  ) -> HashedDiGraph:
    """
    filters out edges and nodes
    """
    excluded_edges = set([] if excluded_edges is None else excluded_edges)
    excluded_nodes = set([] if excluded_nodes is None else excluded_nodes)
    if excluded_edge_type is not None:
        excluded_edges |= {e for e in graph.edges if graph.edges[e].get('type', '') == excluded_edge_type}
    if only_edge_type is not None:
        excluded_edges |= {e for e in graph.edges if graph.edges[e].get('type', '') != only_edge_type}
    if only_nodes is not None:
        excluded_nodes |= {n for n in graph.nodes if n not in only_nodes}
    if only_edges is not None:
        excluded_edges |= {e for e in graph.edges if e not in only_edges}
    r = nx.restricted_view(graph, excluded_nodes, excluded_edges)  # type: HashedDiGraph
    if path_to:
        r = nx.subgraph_view(r, lambda n:  nx.has_path(graph, n, path_to))
    return r


def partial_reverse(G: nx.DiGraph, edges: List[Tuple]) -> HashedDiGraph:
    newG = generic_graph_view(G).copy()
    succ = {}
    pred = {}
    for node in newG.nodes:
        succs = {succ: data for succ, data in newG._succ[node].items() if (node, succ) not in edges}
        succs.update({pred: data for pred, data in newG._pred[node].items() if (pred, node) in edges})
        preds = {pred: data for pred, data in newG._pred[node].items() if (pred, node) not in edges}
        preds.update({succ: data for succ, data in newG._succ[node].items() if (node, succ) in edges})
        succ[node] = succs
        pred[node] = preds
    newG._succ = succ
    newG._pred = pred
    newG._adj = newG._succ
    return newG


@lru_cache()
def get_above_state_traversal_graph(graph: HashedDiGraph):
    """
    traverse backwards and only follow wrt when there is a choice
    """
    wrt_graph = subgraph_view(graph, only_edge_type='wrt')
    def allowed_traversal(a, b):
        if graph.edges[(a, b)]['type'] == 'wrt':
            return True
        if graph.edges[(a, b)]['type'] == 'dep':
            return False
        if wrt_graph.out_degree(b):
            return False  # can't traverse other edges if there is a wrt
        return True
    alloweds = nx.subgraph_view(graph, filter_edge=allowed_traversal)  # type: HashedDiGraph
    return partial_reverse(alloweds, [(a, b) for a, b, data in graph.edges(data=True) if data['type'] != 'wrt'])


def node_dependencies(graph, node):
    dag = subgraph_view(graph, excluded_edge_type='wrt')
    return {n for n in graph.nodes if nx.has_path(dag, n, node)} - {node}
