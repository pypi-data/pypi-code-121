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
from typing import Union

from . import aw_bool_set, aw_data_set, aw_float_set, aw_int_set, aw_string_set
from .enums import ATTRIBUTE_TYPES, AttributeEnum


def write_data(attribute: AttributeEnum, value: Union[int, str, bool, float, bytes] = None) -> None:
    """
    Sets an initialization attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        value (Union[int, str, bool, float, bytes]): The attribute value.

    Raises:
        Exception: If the attribute could not be set.
    """
    aw_type = ATTRIBUTE_TYPES[attribute]

    args = []
    if type(aw_type) == tuple:
        aw_type, *args = aw_type

    switcher = {
        int: aw_int_set,
        str: aw_string_set,
        bool: aw_bool_set,
        float: aw_float_set,
        bytes: aw_data_set
    }

    switcher[aw_type](attribute, value, *args)
