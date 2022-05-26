from typing import Hashable, Tuple, Dict, Container

import networkx as nx


class UniqueEdgeMultiDiGraph(nx.MultiDiGraph):
    """
    Extends the NetworkX MultiDiGraph with useful functions when edge-keys must be unique across all edges.
    """
    def __init__(self, data=None, **attr):
        self._edge_keys_to_nodes: Dict[Hashable, Tuple[Hashable, Hashable]] = {}
        super().__init__(data, **attr)

    def add_edge(self, u_for_edge: Hashable, v_for_edge: Hashable, key: Hashable, **attr) -> Hashable:
        if key in self._edge_keys_to_nodes:
            raise KeyError(f'Edge {key} already existing!')

        super().add_edge(u_for_edge, v_for_edge, key, **attr)

        self._edge_keys_to_nodes[key] = (u_for_edge, v_for_edge)

        return key

    def remove_edge(self, key: Hashable):
        if key not in self._edge_keys_to_nodes:
            raise nx.NetworkXError(f'Edge {key} does not exist.')

        super().remove_edge(*self._edge_keys_to_nodes[key], key)

        del self._edge_keys_to_nodes[key]

    def remove_edges_from(self, ebunch):
        try:
            for e in ebunch:
                self.remove_edge(e)
        except nx.NetworkXError:
            pass

    def merge_nodes(self, nodes: Container[Hashable], newnode: Hashable):
        """
        Merge nodes together into a new node.

        :param nodes:
            The nodes to merge together.
        :param newnode:
            A new node that replaces all nodes to merge unifying all their connections into it.
        """

        if newnode in nodes:
            raise nx.NetworkXError('new node must be distinct from nodes to merge')

        for _, target, key, data in list(self.out_edges(nodes, keys=True, data=True)):
            self.remove_edge(key)
            self.add_edge(newnode, target, key, **data)
        for source, _, key, data in list(self.in_edges(nodes, keys=True, data=True)):
            self.remove_edge(key)
            self.add_edge(source, newnode, key, **data)

        self.remove_nodes_from(nodes)

    def get_nodes(self, edge: Hashable) -> Tuple[Hashable, Hashable]:
        return self._edge_keys_to_nodes[edge]
