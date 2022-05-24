# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
from typing import Any


class AttributeNames(Enum):
    VALUE = "value"


class Altair:
    """
    This class is a data holder to represent Altair charts.
    """

    def __init__(self, value: Any):
        if not hasattr(self.value, "to_json"):
            raise Exception("You must inject an altair chart")
        self.value = value

    def __hash__(self):
        return hash((str(self.value)))

    def __eq__(self, other):
        return (self.value == other.value)

    def __repr__(self):
        ob_repr = f"({AttributeNames.VALUE.value}={self.value})"
        return ob_repr

    def to_dict(self):
        data_dict = dict()
        data_dict[AttributeNames.VALUE.value] = self.value
        return data_dict

    @staticmethod
    def from_dict(dct):
        value = dct[AttributeNames.VALUE.value]
        return Altair(value=value)
