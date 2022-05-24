# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from __future__ import annotations
from enum import Enum
import typing
import uuid

from shapelets.dsl.graph import (
    collapse_into_graph,
    ensure_iterable,
    Graph,
    ordered_output_connections
)
from shapelets.dsl.node import Node

DSLAlgoReturnType = typing.TypeVar('DSLAlgoReturnType',
                                   Node,
                                   typing.List[Node],
                                   typing.Tuple[Node, ...])


class AttributeNames(Enum):
    CUSTOM_GRAPH = "custom-graph"
    CONNECTIONS_ORDER = "connections_order"
    EXECUTE = "execute"
    GRAPH = "graph"
    ON = "on"
    TARGET_RESULT = "targetResult"


class Event:
    @staticmethod
    def add_output_mapping(events: typing.List[Event], from_node: Node, *widget_ids: typing.Tuple[str, ...]):
        output_connector_name = f"output_{from_node.active_output}"
        for event in events:
            for link in event.custom_graph.links:
                if (link.source and not link.destination and
                        link.source.node_id == from_node.node_id and
                        link.source.connector_name == output_connector_name):
                    output_connector_id = f"{from_node.node_id}:{output_connector_name}"
                    recipient_widget_ids = event.outputs_mapping.get(output_connector_id)
                    if not recipient_widget_ids:
                        event.outputs_mapping[output_connector_id] = recipient_widget_ids = []
                    recipient_widget_ids.extend(widget_ids)

    def __init__(self,
                 event_name: str,
                 custom_graph_name: str,
                 custom_graph: Graph = None,
                 connections_order: typing.List[dict] = None):
        self.event_name = event_name
        self.custom_graph_name = custom_graph_name
        self.custom_graph = custom_graph
        self.connections_order = connections_order
        self.outputs_mapping = {}

    @property
    def custom_graph_dict(self):
        return {
            AttributeNames.GRAPH.value: self.custom_graph.to_dict(),
            AttributeNames.CONNECTIONS_ORDER.value: self.connections_order
        }

    def to_dict(self):
        return {
            AttributeNames.ON.value: self.event_name,
            AttributeNames.EXECUTE.value: self.custom_graph_name,
            AttributeNames.TARGET_RESULT.value: self.outputs_mapping if self.outputs_mapping is not None else ""
        }


class EventProducer:
    def __init__(self):
        self.events: typing.List[Event] = []

    def _link_event(self,
                    event_name: str,
                    parent_data_app,
                    algorithm: DSLAlgoReturnType):
        if algorithm is None:
            algorithm_nodes = []
        else:
            algorithm_nodes = ensure_iterable(algorithm)
        custom_graph = collapse_into_graph(algorithm_nodes)
        event = Event(event_name,
                      EventProducer.__unique_graph_name(),
                      custom_graph,
                      ordered_output_connections(algorithm_nodes))
        self.events.append(event)
        parent_data_app.add_custom_graph(event)
        return event

    @staticmethod
    def __unique_graph_name() -> str:
        return f"{AttributeNames.CUSTOM_GRAPH.value}_{uuid.uuid1().int}"
