# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class AttributeNames(Enum):
    DESCRIPTION = 'description'
    GROUP = "Group"
    ID = "id"
    NAME = "name"


class Group:
    def __init__(self,
                 uid: int,
                 name: str,
                 description: str):
        self.uid = uid
        self.name = name
        self.description = description

    def __repr__(self):
        return (f"{AttributeNames.GROUP.value}({AttributeNames.ID.value}={self.uid},"
                f" {AttributeNames.NAME.value}={self.name}, "
                f"{AttributeNames.DESCRIPTION.value}={self.description})")

    def to_dict(self):
        return {
            AttributeNames.ID.value: self.uid,
            AttributeNames.NAME.value: self.name,
            AttributeNames.DESCRIPTION.value: self.description
        }

    @staticmethod
    def from_dict(dct: dict):
        return Group(
            uid=dct[AttributeNames.ID.value],
            name=dct[AttributeNames.NAME.value],
            description=dct[AttributeNames.DESCRIPTION.value])
