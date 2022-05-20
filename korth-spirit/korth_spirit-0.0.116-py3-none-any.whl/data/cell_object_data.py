# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .object_change_data import ObjectChangeData
from .object_create_data import ObjectCreateData


@dataclass(frozen=True)
class CellObjectData:
    type: int
    id: int
    number: int
    owner: int
    build_timestamp: int
    x: int
    y: int
    z: int
    yaw: int
    tilt: int
    roll: int
    model: str
    description: str
    action: str
    # data: bytes

    def set(self, name: str, value: Any) -> "CellObjectData":
        """
        Set the value of the attribute.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.
        """
        from ..sdk import aw_object_change
        
        orig = deepcopy(self.__dict__)
        orig.update({name: value})
        number = orig.pop("number")

        aw_object_change(
            ObjectChangeData(
                **orig,
                old_number=number,
                old_x=orig.get("x"),
                old_z=orig.get("z"),
            )
        )

    @staticmethod
    def create(**kwargs) -> "CellObjectData":
        """
        Create a new CellObjectData instance.

        Args:
            **kwargs: The attributes of the instance.

        Returns:
            CellObjectData: The new CellObjectData instance.
        """
        from ..sdk import aw_object_add

        return CellObjectData(
            **aw_object_add(
                ObjectCreateData(
                    **kwargs
                )
            )
        )
