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
from typing import Dict, List, Tuple, Type

from korth_spirit.sdk import AttributeEnum, EventEnum


class Event:
    def __init__(self, event_type: EventEnum, event_data: List[Tuple[Type, AttributeEnum]]) -> None:
        """
        Class for Active Worlds events, which are published to the bus and simplified for Python.

        Args:
            event_type (EventEnum): The type of event received from the Active Worlds SDK.
            event_data (List[Tuple[Type, AttributeEnum]]): The data associated with the event.
        """
        self.event_type = event_type
        self._translate(event_data)

    def _translate(self, event_data: List[Tuple[Type, AttributeEnum]]) -> None:
        """
        Translates the event data to this object.
        This is a private method.

        Args:
            event_data (List[Tuple[Type, AttributeEnum]]): The data associated with the event.
        """
        from korth_spirit.sdk.get_data import get_data

        for data_type, attribute in event_data:
            name = (
                str(attribute)
                .removeprefix('AttributeEnum.')
                .removeprefix('AW_')
                .lower()
            )
            data = get_data(attribute, data_type)

            setattr(self, name, data)
