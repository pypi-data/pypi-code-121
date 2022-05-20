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
from typing import Type, Union

from . import aw_bool, aw_data, aw_float, aw_int, aw_string
from .enums import ATTRIBUTE_TYPES, AttributeEnum


def get_data(attribute: Union[int, AttributeEnum], aw_type: Type = None) -> Union[int, float, bool, str, bytes, list[bytes]]:
    """
    Gets a data attribute.

    Args:
        attribute (Union[int, AttributeEnum]): The attribute to get.
        aw_type (Type): The type of the attribute. Defaults to None.

    Raises:
        Exception: If the attribute could not be retrieved.
        Exception: If the attribute type is not found.

    Returns:
        Union[int, float, bool, str, bytes]: The attribute value.
    """
    aw_type = ATTRIBUTE_TYPES[attribute]
    
    args = []
    if type(aw_type) == tuple:
        aw_type, *args = aw_type

    switcher = {
        int: aw_int,
        str: aw_string,
        bool: aw_bool,
        float: aw_float,
        bytes: aw_data
    }

    return switcher[aw_type](attribute, *args)
