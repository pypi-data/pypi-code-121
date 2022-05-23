#   Copyright 2022-2022 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from pprint import pformat
from typing import Any, Dict, List, Union

from th2_common_utils.converters import _dict_to_message_convert_value, message_to_dict, TypeName
from th2_common_utils.util.common import SimpleType
from th2_grpc_common.common_pb2 import ListValue, Message, Value


# =========================
# Value
# =========================

def value_get(self: Value, item: SimpleType) -> Union[str, ListValue, Message]:
    return getattr(self, self.WhichOneof('kind'))  # type: ignore


setattr(Value, '__get__', value_get)


# =========================
# ListValue
# =========================

def listvalue_getitem(self: ListValue, index: int) -> Union[str, List, Dict]:
    value = self.values[index]
    return value.__get__(index)  # type: ignore


def listvalue_len(self: ListValue) -> int:
    return len(self.values)


setattr(ListValue, '__getitem__', listvalue_getitem)
setattr(ListValue, '__len__', listvalue_len)


# =========================
# Message
# =========================

def message_setitem(self: Message, key: str, value: Any) -> None:
    value_type = type(value).__name__

    if value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        self.fields[key].simple_value = str(value)

    elif value_type == TypeName.VALUE:
        self.fields[key].simple_value = value.simple_value

    elif value_type in {TypeName.LIST, TypeName.LIST_VALUE}:
        th2_value = _dict_to_message_convert_value(value)
        self.fields[key].list_value.CopyFrom(th2_value.list_value)

    elif value_type in {TypeName.DICT, TypeName.MESSAGE}:
        th2_value = _dict_to_message_convert_value(value)
        self.fields[key].message_value.CopyFrom(th2_value.message_value)

    else:
        raise TypeError('Cannot set %s object as field value.' % value_type)


def message_getitem(self: Message, item: str) -> Union[str, List, Dict]:
    if item in self.fields:
        value = self.fields[item]
        return value.__get__(item)  # type: ignore
    else:
        raise KeyError(item)


def message_contains(self: Message, item: str) -> bool:
    return item in self.fields


def message_repr(self: Message) -> str:
    return pformat(message_to_dict(self))


setattr(Message, '__setitem__', message_setitem)
setattr(Message, '__getitem__', message_getitem)
setattr(Message, '__contains__', message_contains)
setattr(Message, '__repr__', message_repr)
