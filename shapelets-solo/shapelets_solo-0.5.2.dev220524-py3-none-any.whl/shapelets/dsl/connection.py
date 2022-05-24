# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import uuid


class AttributeNames(Enum):
    CHILD_OF = "child-of"
    CONNECTION = "Connection"
    CONNECTOR_ID = "connector_id"
    ID = "id"
    INDEX = "@index"
    NODE_ID = "node_id"
    PARAM_INDEX = "param_index"
    PARENT_CONNECTOR_ID = "parent_connector_id"


class Connection:
    def __init__(self,
                 node_id: uuid.UUID,
                 connector_name: str,
                 parent_connector_name: str = None,
                 param_index: int = None):
        self.node_id = node_id
        self.connector_name = connector_name
        # If the connection id points to a flow the parent_connection_id
        # tracks the relationship between the node within the flow and the
        # node representing the flow
        self.parent_connector_name = parent_connector_name
        # If the connection id points to a flow the param_index tracks the
        # order of the parameter in the generated DSL
        self.param_index = param_index

    def __hash__(self):
        return hash((self.node_id,
                     self.connector_name,
                     self.parent_connector_name,
                     self.param_index))

    def __eq__(self, other) -> bool:
        return (isinstance(other, Connection) and
                self.node_id == other.node_id and
                self.connector_name == other.connector_name and
                self.parent_connector_name == other.parent_connector_name and
                self.param_index == other.param_index)

    def to_dict(self) -> dict:
        p_idx = int(self.param_index) if self.param_index is not None else None
        return {
            AttributeNames.NODE_ID.value: str(self.node_id),
            AttributeNames.CONNECTOR_ID.value: {
                AttributeNames.ID.value: self.connector_name,
                AttributeNames.PARENT_CONNECTOR_ID.value: self.parent_connector_name,
                AttributeNames.PARAM_INDEX.value: p_idx
            }
        }

    @staticmethod
    def from_dict(input_: dict):
        return Connection(
            uuid.UUID(input_[AttributeNames.NODE_ID.value]),
            input_[AttributeNames.CONNECTOR_ID.value][AttributeNames.ID.value],
            input_[AttributeNames.CONNECTOR_ID.value][AttributeNames.PARENT_CONNECTOR_ID.value],
            input_[AttributeNames.CONNECTOR_ID.value][AttributeNames.PARAM_INDEX.value])

    def __repr__(self):
        s_repr = f"{AttributeNames.CONNECTION.value}{{{AttributeNames.NODE_ID.value}:{self.node_id}, "
        s_repr += f"{AttributeNames.CONNECTOR_ID.value}:{self.connector_name}"
        if self.parent_connector_name and self.param_index:
            s_repr += f" {AttributeNames.CHILD_OF.value} {self.parent_connector_name}"
            s_repr += f" {AttributeNames.INDEX.value} {self.param_index}"
        s_repr += f"}}"
        return s_repr
