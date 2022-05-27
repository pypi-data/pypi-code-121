import json
from typing import Type, List

from tokyo_annotation.utils import DiGraph
from tokyo_annotation.models.node import Node, DataNode, JobNode

class Lineage:
    def __init__(
        self,
        graph: DiGraph):
        self._graph = graph

    @property
    def graph(self):
        return self._graph


def get_upstream(
        node: Type[Node],
        lineage: Lineage
    ) -> List[Type[Node]]:
        index = lineage.graph.nodes.get_key(node)
        upstreams = lineage.graph.get_upstream(index)

        return upstreams


def get_upstream_recursive(
        node: Type[Node],
        lineage: Lineage
    ):
        upstreams = get_upstream(node, lineage)

        all_upstreams = []
        all_upstreams += upstreams

        for i in upstreams:
            all_upstreams += get_upstream_recursive(i, lineage)
        
        return all_upstreams


def get_downstream(
        node: Type[Node],
        lineage: Lineage
    ):
        index = lineage.graph.nodes.get_key(node)
        downstreams = lineage.graph.get_downstream(index)

        return downstreams


def get_downstream_recursive(
        node: Type[Node],
        lineage: Lineage
    ):
        downstreams = get_downstream(node, lineage)

        all_downstreams = []
        all_downstreams += downstreams

        for i in downstreams:
            all_downstreams += get_downstream_recursive(i, lineage)
        
        return all_downstreams


def parse_raw_lineage(
    lineage: str
) -> Lineage:
    parsed = json.loads(lineage)

    _graph = parsed['graph']
    graph = DiGraph()

    # Register all nodes in graph
    for node in _graph:
        node_type = DataNode if node['type'] == 'DATASET' else JobNode
        graph.add(
            node_type(node['id'], node['type'], node['data'])
        )

    # Connect node's edges
    nodes = graph.nodes.map

    def _get_key_from_id(id, nodes: dict):
        for k, node in nodes.items():
            if node.id == id:
                return k

    for node in _graph:
        in_edges = [edge['origin'] for edge in node['inEdges']]
        out_edges = [edge['destination'] for edge in node['outEdges']]

        current_node_key = _get_key_from_id(node['id'], nodes)

        for id in in_edges:
            node_key = _get_key_from_id(id, nodes)
            graph.set_edge(node_key, current_node_key, True)

        for id in out_edges:
            node_key = _get_key_from_id(id, nodes)
            graph.set_edge(current_node_key, node_key, True)

    return Lineage(graph)


def get_genesis_datasets(
    node: Node,
    lineage: Lineage
) -> List[Node]:
    upstreams = get_upstream_recursive(node, lineage)

    genesis = []

    for upstream in upstreams:
        if get_upstream(upstream, lineage) == []:
            genesis.append(upstream)
    
    return genesis