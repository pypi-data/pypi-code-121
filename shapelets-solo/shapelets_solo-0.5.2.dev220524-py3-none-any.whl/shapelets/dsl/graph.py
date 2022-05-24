# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from __future__ import annotations
from collections.abc import Iterable
from enum import Enum
import numpy
import typing
import uuid


from shapelets.dsl.connection import Connection
from shapelets.dsl.link import Link
from shapelets.dsl.node import InputParameter, Node
from shapelets.model import View, ViewGroupEntry, Match, Sequence


class AttributeNames(Enum):
    CUSTOM_GRAPH = "custom-graph"
    LINKS = "links"
    NODES = "nodes"


# an extension of shapelets.dsl.argument_types.SupportedTypes
Types = typing.TypeVar(
    'NodeInputParamTypes',
    numpy.ndarray,
    View, ViewGroupEntry, Match, Sequence,
    bool, bytes, float, int, str,
    typing.Callable,
    typing.List,
    Node,
    InputParameter)

NodeInputParamType = typing.Generic[Types]
NodeReturnType = typing.TypeVar('NodeReturnType', Node, typing.Tuple[Node, ...])


def ensure_iterable(nodes: NodeReturnType):
    return nodes if isinstance(nodes, Iterable) else (nodes,)


class Graph(Node):

    @staticmethod
    def unique_graph_id() -> str:
        return f"{AttributeNames.CUSTOM_GRAPH.value}_{uuid.uuid1().int}"

    def __init__(self, graph_id: str = None):
        super().__init__("graph")
        self.node_id = graph_id if graph_id else Graph.unique_graph_id()

    def add_output_node(self, idx: int, parent_name: str, node: Node):
        self._extend_from_input_param_node(node)
        out_connector_name = node.active_out_connector().connector_name
        self._add_link(Link(Connection(node.node_id, out_connector_name, parent_name, idx), None))

    def validate(self):
        self._validate_links()

    def to_dict(self) -> dict:
        return {
            AttributeNames.NODES.value: [node.to_dict() for node in self.source_nodes],
            AttributeNames.LINKS.value: [link.to_dict() for link in self.links]
        }


def ordered_output_connections(output_nodes: NodeReturnType) -> typing.List[str]:
    ordered_connections = []
    nodes = ensure_iterable(output_nodes)
    for node in nodes:
        out_connector_name = node.active_out_connector().connector_name
        conn = Connection(node.node_id, out_connector_name).to_dict()
        ordered_connections.append(conn)
    return ordered_connections


def collapse_into_graph(output_nodes: NodeReturnType,
                        parent_names: typing.List[str] = None) -> Graph:
    nodes = ensure_iterable(output_nodes)
    if parent_names:
        names = ensure_iterable(parent_names)
        if len(names) != len(nodes):
            raise ValueError("invalid number of names")
    else:
        names = [None] * len(nodes)
    graph = Graph()
    for idx, (name, node) in enumerate(zip(names, nodes)):
        graph.add_output_node(idx, name, node)
    graph.validate()
    return graph
