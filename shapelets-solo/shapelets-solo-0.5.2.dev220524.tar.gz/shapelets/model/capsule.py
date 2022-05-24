# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import dill


class AttributeNames(Enum):
    DATA = "data"
    NAME = "name"


class Capsule:
    """
    This class is a data holder to represent Shapelets Capsules.
    """

    def __init__(self,
                 data,
                 name: str = None):
        self.name = name
        self.data = data

    def __hash__(self):
        return hash((str(self.data),
                     self.name,
                     ))

    def __eq__(self, other):
        return (isinstance(other, Capsule) and
                self.data == other.data and
                self.name == other.name)

    def __repr__(self):
        ob_repr = f"({AttributeNames.DATA.value}={self.data}, "
        ob_repr += f"{AttributeNames.NAME.value}={self.name})"
        return ob_repr

    def to_dict(self):
        data_dict = dict()
        if self.name:
            data_dict[AttributeNames.NAME.value] = self.name
        data_dict[AttributeNames.DATA.value] = str(base64.b64encode(dill.dumps(self.data)), encoding='utf-8')
        return data_dict

    @staticmethod
    def from_dict(dct):
        data = dill.loads(base64.decodebytes(bytes(dct[AttributeNames.DATA.value], encoding="utf-8")))
        return Capsule(
            data=data,
            name=dct[AttributeNames.NAME.value])
