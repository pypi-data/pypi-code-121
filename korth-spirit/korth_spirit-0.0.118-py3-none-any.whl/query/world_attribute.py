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
from typing import Iterable

from ..data import AttributeData
from ..sdk import AttributeEnum
from ..sdk.enums import ATTRIBUTE_TYPES
from ..sdk.get_data import get_data
from .world_attribute_enum import WorldAttributeEnum


class WorldAttributeQuery:
    def __init__ (self, instance: "Instance") -> None:
        """
        Initializes the attribute query.
        
        Args:
            instance (Instance): The instance to query.
        """
        self.instance = instance

    def query_specific(self, **kwargs) -> AttributeData:
        """
        Queries the world for the specified attribute.

        Args:
            attribute (Union[str, WorldAttributeEnum]): The attribute to query.

        Returns:
            Iterable[AttributeData]: The queried attribute.
        """
        attribute = kwargs.get('attribute')

        if isinstance(attribute, str):
            attribute = f'AW_WORLD_{attribute.upper()}'
            attribute = WorldAttributeEnum(attribute)

        return AttributeData(
            name=attribute.name,
            value=get_data(attribute),
            typed=ATTRIBUTE_TYPES[attribute.type]
        )

    def query_all(self) -> Iterable[AttributeData]:
        """
        Queries the world for all attributes.

        Returns:
            Iterable[AttributeData]: The queried attributes.
        """
        for attribute in WorldAttributeEnum:
            attribute = AttributeEnum(attribute.value)
            yield AttributeData(
                name=attribute.name,
                value=get_data(attribute),
                typed=ATTRIBUTE_TYPES[attribute]
            )

    def query(self, **kwargs) -> Iterable[AttributeData]:
        """
        Queries the world for the specified attribute.
        If is not specified, queries all attributes.

        Args:
            attribute (Union[str, WorldAttributeEnum]): The attribute to query.

        Returns:
            Iterable[AttributeData]: The queried attribute.
        """
        if 'attribute' in kwargs:
            return self.query_specific(**kwargs)
        
        return self.query_all()
