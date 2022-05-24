# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
from typing import Optional
import uuid

from shapelets.dsl.connection import Connection


class AttributeNames(Enum):
    DESTINATION = "destination"
    ID = "id"
    LINK = "Link"
    LINK_ID = "link_id"
    SOURCE = "source"


class Link:
    def __init__(self, source: Optional[Connection], destination: Optional[Connection]):
        self.link_id = uuid.uuid4()
        self.source = source
        self.destination = destination

    def __eq__(self, other) -> bool:
        return (isinstance(other, Link) and
                self.link_id == other.link_id)

    def __hash__(self) -> int:
        return hash(self.link_id)

    def to_dict(self) -> dict:
        return {
            AttributeNames.ID.value: str(self.link_id),
            AttributeNames.SOURCE.value: self.source.to_dict() if self.source else None,
            AttributeNames.DESTINATION.value: self.destination.to_dict() if self.destination else None
        }

    @staticmethod
    def from_dict(input_: dict):
        source = input_[AttributeNames.SOURCE.value]
        if source:
            source = Connection.from_dict(source)
        destination = input_[AttributeNames.DESTINATION.value]
        if destination:
            destination = Connection.from_dict(destination)
        link = Link(source, destination)
        link.link_id = uuid.UUID(input_[AttributeNames.ID.value])
        return link

    def __repr__(self):
        s_repr = f"{AttributeNames.LINK.value}{{{AttributeNames.LINK_ID.value}:{self.link_id}, "
        s_repr += f"{AttributeNames.SOURCE.value}:{self.source}, "
        s_repr += f"{AttributeNames.DESTINATION.value}:{self.destination}}}"
        return s_repr
