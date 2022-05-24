# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from __future__ import annotations
from copy import copy
from enum import Enum
import uuid
import typing

import shapelets.dsl.dsl_op as dsl_op
from shapelets.dsl.argument_types import (
    ArgumentTypeEnum,
    ArgumentType,
    ArgumentValue,
    argument_type_for,
    compatible_types_pred,
    is_numeric,
    is_sequence,
    SupportedTypes
)
from shapelets.dsl.connection import Connection
from shapelets.dsl.connector import Connector
from shapelets.dsl.exceptions import (
    ConnectorNotFound,
    MalformedGraph,
    NodeNotFound,
    NodeOperationNotSupported
)
from shapelets.dsl.link import Link


class AttributeNames(Enum):
    ACTIVE_OUTPUT = "active_output"
    CONNECTOR_NAME = "data"
    ID = "id"
    IN_CONN = "in_conn"
    LINKS = "links"
    NODE = "Node"
    OPERATION = "operation"
    OUT_CONN = "out_conn"
    SOURCE_NODES = "source_nodes"
    VALUE = "value"
    WIDGET_ID = "widget_id"


class InputParameter:
    def __init__(self, index: int, name: str):
        self.index = index
        self.name = name

    def __repr__(self):
        return f"arg{self.index}:{self.name!r}"


class NodeType(Enum):
    SourceNode = 0,
    WidgetNode = 1,
    Node = 2


class Node:
    def __init__(self, operation: str, node_type: NodeType = NodeType.Node):
        self.node_id: uuid.UUID = uuid.uuid4()
        self.operation: str = operation
        self.node_type = node_type
        self.source_nodes: typing.List[Node] = []
        self.links: typing.List[Link] = []
        self.in_connectors: typing.List[Connector] = []
        self.out_connectors: typing.List[Connector] = []
        self.active_output: int = 0

    def add_input_param(self,
                        param_value: typing.Generic[SupportedTypes],
                        param_name: str,
                        *param_type: typing.Tuple[ArgumentTypeEnum, ...]):
        self.in_connectors.append(Connector(param_name, ArgumentType(*param_type)))
        connector_id = param_name
        parent_connector_id = None
        param_index = 0
        if isinstance(param_value, Node):
            node = param_value
            if param_value.node_type == NodeType.WidgetNode:
                self._add_source_node(node)
                node.out_connectors.append(Connector(node.operation, param_value.value_type))
                connection = Connection(node.node_id, node.operation)
            else:
                # If it is already a node, add its accumulated graph and create the connection
                self._extend_from_input_param_node(node)
                connector_name = node.active_out_connector().connector_name
                connection = Connection(node.node_id, connector_name)
        elif isinstance(param_value, InputParameter):
            # If it is a registrar set the connection to None and update the name
            connection = None
            parent_connector_id = param_value.name
            param_index = param_value.index
        else:
            # If it is not one of the above then it is a Initializer. Create a node for
            # it with just one output connector and create a connection to connector
            # named "data"
            connector_name = AttributeNames.CONNECTOR_NAME.value
            argument_type = ArgumentType(*param_type)
            node = SourceNode(ArgumentValue(argument_type, param_value))
            self._add_source_node(node)
            node.out_connectors.append(Connector(connector_name, argument_type))
            connection = Connection(node.node_id, connector_name)
        self._add_link(Link(
            connection,
            Connection(self.node_id, connector_id, parent_connector_id, param_index)))

    def add_output_connector(self,
                             output_index: int,
                             param_name: str,
                             *param_type: typing.Tuple[ArgumentTypeEnum, ...]):
        self.out_connectors.append(Connector(param_name, ArgumentType(*param_type)))
        if output_index == 0:
            return self
        copy_of_self = copy(self)
        copy_of_self.active_output = output_index
        return copy_of_self

    def active_out_connector(self) -> Connector:
        if not self.out_connectors:
            raise ConnectorNotFound(
                f"no output connectors at Node('{self.operation}').id: {self.node_id}")
        return self.out_connectors[self.active_output]

    def active_return_type(self) -> ArgumentType:
        connector = self.active_out_connector()
        return connector.connector_type

    def to_dict(self) -> dict:
        my_dict = {
            AttributeNames.ID.value: str(self.node_id),
            AttributeNames.OPERATION.value: self.operation
        }
        if hasattr(self, AttributeNames.WIDGET_ID.value):
            my_dict[AttributeNames.VALUE.value] = self.widget_id
        return my_dict

    @staticmethod
    def from_dict(input_: dict):
        node = Node(input_[AttributeNames.OPERATION.value])
        node.node_id = uuid.UUID(input_[AttributeNames.ID.value])
        return node

    def __hash__(self) -> int:
        return hash((self.node_id, self.operation))

    def __eq__(self, other) -> bool:
        return (isinstance(other, Node) and
                self.node_id == other.node_id and
                self.operation == other.operation)

    def __repr__(self):
        s_repr = f"{AttributeNames.NODE.value}{{{AttributeNames.ID.value}:{self.node_id}, "
        s_repr += f"{AttributeNames.OPERATION.value}:'{self.operation}', "
        s_repr += f"{AttributeNames.ACTIVE_OUTPUT.value}:{self.active_output}, "
        s_repr += f"{AttributeNames.IN_CONN.value}:{self.in_connectors}, "
        s_repr += f"{AttributeNames.OUT_CONN.value}:{self.out_connectors}, "
        s_repr += f"{AttributeNames.SOURCE_NODES.value}:{self.source_nodes}, "
        s_repr += f"{AttributeNames.LINKS.value}:{self.links}}}"
        return s_repr

    def _add_source_node(self, source_node: Node):
        self.source_nodes.append(source_node)
        self._remove_duplicates()

    def _add_link(self, link: Link):
        self.links.append(link)
        self._validate_link(link)
        self._remove_duplicates()

    def _extend_from_input_param_node(self, node: Node):
        self.source_nodes.append(node)
        self.source_nodes.extend(node.source_nodes)
        self.links.extend(node.links)
        self._remove_duplicates()

    def _validate_links(self):
        for link in self.links:
            self._validate_link(link)

    def _validate_link(self, link: Link):
        if link.source and link.destination:
            src_type = self.__get_link_src_type(link)
            dst_type = self.__get_link_dst_type(link)
            if not compatible_types_pred(src_type, dst_type):
                err_msg = f"Connection types {src_type.get_all_values()} "
                err_msg += f"and {dst_type.get_all_values()} don't match"
                raise MalformedGraph(err_msg)

    def _remove_duplicates(self):
        self.source_nodes = Node.__filter_duplicates(self.source_nodes)
        self.links = Node.__filter_duplicates(self.links)

    @staticmethod
    def __filter_duplicates(container):
        ret = []
        ret_hashes = []
        for item in container:
            item_hash = hash(item)
            if item_hash not in ret_hashes:
                ret_hashes.append(item_hash)
                ret.append(item)
        return ret

    def __get_link_src_type(self, link: Link) -> ArgumentType:
        connection = link.source
        connectors = self.__find_node_by_id(connection.node_id).out_connectors
        return Node.__connector_type(connection, connectors)

    def __get_link_dst_type(self, link: Link) -> ArgumentType:
        connection = link.destination
        connectors = self.__find_node_by_id(connection.node_id).in_connectors
        return Node.__connector_type(connection, connectors)

    def __find_node_by_id(self, node_id: uuid.UUID):
        if self.node_id == node_id:
            return self
        node = next(filter(lambda node_i: node_i.node_id == node_id, self.source_nodes), None)
        if not node:
            raise NodeNotFound(f"node with id {node_id} not found")
        return node

    @staticmethod
    def __connector_type(target_connector: Connector, connectors: typing.List[Connector]) -> ArgumentType:
        connector_name = target_connector.connector_name
        connector = next(filter(lambda conn_i: conn_i.connector_name == connector_name, connectors), None)
        if not connector:
            raise ConnectorNotFound(f"connector by name [{connector_name}] not found")
        return connector.connector_type

    # https://docs.python.org/3.7/library/operator.html

    def __add__(self, other):
        if isinstance(other, Node):
            self_type = self.active_return_type()
            other_type = other.active_return_type()
            if self_type.is_numeric() and other_type.is_numeric():
                return dsl_op.plus(self, other)
            if self_type.is_sequence() and other_type.is_numeric():
                return dsl_op.plus_ts(self, other)
            if self_type.is_numeric() and other_type.is_sequence():
                return dsl_op.plus_ts(other, self)
            if self_type.is_sequence() and other_type.is_sequence():
                return dsl_op.plus_ts_ts(self, other)
            raise NodeOperationNotSupported(
                f"{self_type} + {other_type} is not supported")
        return self.__radd__(other)

    def __radd__(self, other):
        self_type = self.active_return_type()
        if self_type.is_numeric() and is_numeric(other):
            return dsl_op.plus(self, other)
        if self_type.is_sequence() and is_numeric(other):
            return dsl_op.plus_ts(self, other)
        if self_type.is_numeric() and is_sequence(other):
            return dsl_op.plus_ts(other, self)
        if self_type.is_sequence() and is_sequence(other):
            return dsl_op.plus_ts_ts(self, other)
        raise NodeOperationNotSupported(
            f"{self_type} + {argument_type_for(other)} is not supported")

    def __mul__(self, other):
        if isinstance(other, Node):
            self_type = self.active_return_type()
            other_type = other.active_return_type()
            if self_type.is_numeric() and other_type.is_numeric():
                return dsl_op.times(self, other)
            if self_type.is_sequence() and other_type.is_numeric():
                return dsl_op.times_ts(self, other)
            if self_type.is_numeric() and other_type.is_sequence():
                return dsl_op.times_ts(other, self)
            if self_type.is_sequence() and other_type.is_sequence():
                return dsl_op.times_ts_ts(self, other)
            raise NodeOperationNotSupported(
                f"{self_type} + {other_type} is not supported")
        return self.__rmul__(other)

    def __rmul__(self, other):
        self_type = self.active_return_type()
        if self_type.is_numeric() and is_numeric(other):
            return dsl_op.times(self, other)
        if self_type.is_sequence() and is_numeric(other):
            return dsl_op.times_ts(self, other)
        if self_type.is_numeric() and is_sequence(other):
            return dsl_op.times_ts(other, self)
        if self_type.is_sequence() and is_sequence(other):
            return dsl_op.times_ts_ts(self, other)
        raise NodeOperationNotSupported(
            f"{self_type} + {argument_type_for(other)} is not supported")


class SourceNode(Node):
    OPERATION = "initializer"

    def __init__(self, argument_value: ArgumentValue):
        super().__init__(SourceNode.OPERATION, node_type=NodeType.SourceNode)
        self.node_id = hash(argument_value)  # not a UUID, but a long, to make it easily distinguishable (I guess)
        self.value = argument_value

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.value))

    def __eq__(self, other) -> bool:
        return (isinstance(other, SourceNode) and
                super().__eq__(other) and
                self.value == other.value)

    def to_dict(self) -> dict:
        res_dict = super().to_dict()
        res_dict[AttributeNames.VALUE.value] = self.value.to_dict()
        return res_dict

    @staticmethod
    def from_dict(input_: dict):
        input_value = input_["value"]
        source_node = SourceNode(ArgumentValue.from_dict(input_value))
        source_node.node_id = uuid.UUID(input_[AttributeNames.ID.value])
        return source_node

    def __repr__(self):
        s_repr = super().__repr__().replace('Node{id:', 'SourceNode{id:')
        s_repr += f".{AttributeNames.VALUE.value}: {self.value}"
        return s_repr
