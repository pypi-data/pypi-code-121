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


import enum
from typing import Any, Dict, List, Optional, Union

from google.protobuf.duration_pb2 import Duration
from th2_common_utils.util.tree_table import Table, TreeTable
from th2_grpc_common.common_pb2 import ConnectionID, EventID, ListValue, ListValueFilter, Message, \
    MessageFilter, MessageID, MessageMetadata, MetadataFilter, RootComparisonSettings, RootMessageFilter, \
    SimpleList, Value, ValueFilter


class ValueType(str, enum.Enum):

    SIMPLE: str = 'simple_value'
    LIST: str = 'list_value'
    MESSAGE: str = 'message_value'


class TypeName(str, enum.Enum):

    STR = 'str'
    INT = 'int'
    FLOAT = 'float'
    LIST = 'list'
    DICT = 'dict'

    VALUE = 'Value'
    LIST_VALUE = 'ListValue'
    MESSAGE = 'Message'

    VALUE_FILTER = 'ValueFilter'


DictMessageType = Union[str, List, Dict]


def _message_to_dict_convert_value(value: Value) -> Optional[DictMessageType]:
    value_kind = value.WhichOneof('kind')

    if value_kind == ValueType.SIMPLE:
        return value.simple_value  # type: ignore
    elif value_kind == ValueType.LIST:
        return [_message_to_dict_convert_value(list_item) for list_item in value.list_value.values]
    elif value_kind == ValueType.MESSAGE:
        return {
            field: _message_to_dict_convert_value(value.message_value.fields[field])
            for field in value.message_value.fields
        }

    return None


def message_to_dict(message: Message) -> Dict[str, Optional[DictMessageType]]:
    """Converts th2-message to a dict.

    Fields of th2-message will be converted to a dict. You will lose all metadata.

    Args:
        message: th2-message.

    Returns:
        th2-message fields (message.fields) as a dict. All nested entities will be also converted.

        Conversion rules:
            Value.simple_value - str
            Value.list_value - list
            Value.message_value - dict

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    return {field: _message_to_dict_convert_value(message.fields[field]) for field in message.fields}


def _dict_to_message_convert_value(value: Any) -> Value:
    value_type = type(value).__name__

    if value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return Value(simple_value=str(value))
    elif value_type == TypeName.LIST:
        return Value(list_value=ListValue(values=[_dict_to_message_convert_value(x) for x in value]))
    elif value_type == TypeName.DICT:
        return Value(message_value=Message(fields={key: _dict_to_message_convert_value(value[key]) for key in value}))

    elif value_type == TypeName.VALUE:
        return value  # type: ignore
    elif value_type == TypeName.LIST_VALUE:
        return Value(list_value=value)
    elif value_type == TypeName.MESSAGE:
        return Value(message_value=value)

    else:
        raise TypeError('Cannot convert %s object.' % value_type)


def dict_to_message(fields: dict,
                    parent_event_id: Optional[EventID] = None,
                    session_alias: str = '',
                    message_type: str = '') -> Message:
    """Converts a dict to th2-message with 'metadata' and 'parent_event_id'.

    Args:
        fields: Message fields as a dict.
        parent_event_id: Parent event id.
        session_alias: Session alias (is used when creating message metadata).
        message_type: Message type (is used when creating message metadata).

    Returns:
        th2-message with 'metadata' and 'parent_event_id'. All 'fields' nested entities will be converted.

        Conversion rules:
            str, int, float, Value - Value.simple_value
            list, ListValue - Value.list_value
            dict, Message - Value.message_value.

    Raises:
        TypeError: Occurs when 'message.fields' contains a field of the unsupported type.
    """

    if parent_event_id is None:
        parent_event_id = EventID()

    return Message(parent_event_id=parent_event_id,
                   metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias=session_alias)),
                                            message_type=message_type),
                   fields={field: _dict_to_message_convert_value(fields[field]) for field in fields})


def _convert_metadata_filter_value(value: Any) -> Union[MetadataFilter.SimpleFilter]:
    value_type = type(value).__name__

    if value_type == TypeName.VALUE_FILTER:
        return value  # type: ignore

    elif value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return MetadataFilter.SimpleFilter(value=str(value))

    elif value_type == TypeName.LIST:
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=value))

    else:
        raise TypeError('Cannot convert %s object.' % type(value))


def _convert_message_filter_value(value: Any,
                                  message_type: str = '',
                                  direction: str = '') -> ValueFilter:
    value_type = type(value).__name__

    if value_type == TypeName.VALUE_FILTER:
        return value  # type: ignore

    elif value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return ValueFilter(simple_filter=str(value))

    elif value_type == TypeName.LIST:
        return ValueFilter(list_filter=ListValueFilter(
            values=[_convert_message_filter_value(x) for x in value])
        )

    elif value_type == TypeName.DICT:
        return ValueFilter(
            message_filter=MessageFilter(messageType=message_type,
                                         fields={
                                             key: _convert_message_filter_value(value[key])
                                             for key in value
                                         },
                                         direction=direction))
    else:
        raise TypeError('Cannot convert %s object.' % type(value))


def dict_to_root_message_filter(message_type: str = '',
                                message_filter: Optional[Union[Dict, MessageFilter]] = None,
                                metadata_filter: Optional[Union[Dict, MetadataFilter]] = None,
                                ignore_fields: Optional[List[str]] = None,
                                check_repeating_group_order: bool = False,
                                time_precision: Optional[Duration] = None,
                                decimal_precision: str = '') -> RootMessageFilter:
    """Converts a dict to root message filter.

    Args:
        message_type: Message type.
        message_filter: Message filter as a dict or MessageFilter class instance.
        metadata_filter: Metadata filter as a dict or MetadataFilter class instance.
        ignore_fields: Fields to ignore (is used when creating filter's comparison settings).
        check_repeating_group_order: Whether check repeating group order or not (is used when creating filter's
            comparison settings).
        time_precision: Time precision (is used when creating filter's comparison settings).
        decimal_precision: Decimal Precision (is used when creating filter's comparison settings).

    Returns:
        Root message filter class instance.

    Raises:
        TypeError: Occurs when MessageFilter or MetadataFilter as dicts contain a field of the unsupported type.
    """

    if message_filter is None:
        message_filter = MessageFilter()
    elif isinstance(message_filter, Dict):
        message_filter = MessageFilter(fields={
            field: _convert_message_filter_value(message_filter[field])
            for field in message_filter
        })

    if metadata_filter is None:
        metadata_filter = MetadataFilter()
    elif isinstance(metadata_filter, Dict):
        metadata_filter = MetadataFilter(property_filters={
            value: _convert_metadata_filter_value(metadata_filter[value])
            for value in metadata_filter
        })

    return RootMessageFilter(messageType=message_type,
                             message_filter=message_filter,
                             metadata_filter=metadata_filter,
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))


def _message_to_table_convert_value(message_value: Union[str, List, Dict],
                                    columns_names: List[str]) -> Optional[Union[str, Table]]:
    value_type = type(message_value).__name__

    if value_type == TypeName.STR:
        return message_value  # type: ignore

    elif value_type == TypeName.LIST:
        table = Table(columns_names)

        for index, list_item in enumerate(message_value):
            table_inner_item = _message_to_table_convert_value(list_item, columns_names)
            if isinstance(table_inner_item, Table):
                table.add_table(index, table_inner_item)
            else:
                table.add_row(index, table_inner_item)

        return table

    elif value_type == TypeName.DICT:
        table = Table(columns_names)

        for field_name, field_value in message_value.items():  # type: ignore
            table_inner_item = _message_to_table_convert_value(field_value, columns_names)
            if isinstance(table_inner_item, Table):
                table.add_table(field_name, table_inner_item)
            else:
                table.add_row(field_name, table_inner_item)

        return table

    else:
        raise TypeError('Expected object type of str, int, float, list or dict, got %s' % type(message_value))


def message_to_table(message: Union[Dict, Message]) -> TreeTable:
    """Converts th2-message or dict to a tree table.

    Table can have only two columns. Nested tables are allowed. You will lose 'parent_event_id' and 'metadata'
    of the message.

    Args:
        message: th2-message.

    Returns:
        Tree table with two columns - one contains the name of the field and the other contains the value of this field.

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    if isinstance(message, Message):
        message = message_to_dict(message)

    table = TreeTable(columns_names=['Field Value'])

    for field_name in message:
        table_entity = _message_to_table_convert_value(message[field_name], table.columns_names)  # type: ignore
        if isinstance(table_entity, Table):
            table.add_table(field_name, table_entity)
        else:
            table.add_row(field_name, table_entity)

    return table
