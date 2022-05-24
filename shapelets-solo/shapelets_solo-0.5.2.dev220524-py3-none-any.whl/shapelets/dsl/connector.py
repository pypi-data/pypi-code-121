# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum

from shapelets.dsl.argument_types import ArgumentType, ArgumentTypeEnum


class AttributeNames(Enum):
    CONNECTOR = "Connector"
    NAME = "name"
    TYPE = "type"


class Connector:
    def __init__(self, connector_name: str, connector_type: ArgumentType):
        self.connector_name = connector_name
        self.connector_type = connector_type

    def __hash__(self):
        return hash((self.connector_name, self.connector_type))

    def __eq__(self, other):
        return (isinstance(other, Connector) and
                self.connector_name == other.connector_name and
                self.connector_type == other.connector_type)

    def to_dict(self) -> dict:
        return {
            "name": self.connector_name,
            "type": self.connector_type.get_all_values()
        }

    @staticmethod
    def from_dict(input_: dict):
        input_types_str = input_[AttributeNames.TYPE.value].split(ArgumentType.SEP)
        input_types = (ArgumentTypeEnum(item) for item in input_types_str)
        return Connector(input_[AttributeNames.NAME.value], ArgumentType(*input_types))

    def __repr__(self):
        return f"{AttributeNames.CONNECTOR.value}{{'{self.connector_name}':{self.connector_type}}}"
