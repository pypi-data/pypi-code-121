#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
FastyBird MQTT connector registry module records
"""

# Python base dependencies
import uuid
from datetime import datetime
from typing import List, Optional, Set, Tuple, Union

# Library dependencies
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload


class DeviceRecord:  # pylint: disable=too-many-instance-attributes
    """
    Device record

    @package        FastyBird:FbMqttConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID

    __identifier: str
    __name: Optional[str]

    __state: ConnectionState = ConnectionState.UNKNOWN

    __controls: Set[str] = set()

    __last_communication_timestamp: Optional[float] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str],
        device_state: ConnectionState = ConnectionState.UNKNOWN,
        controls: Union[List[str], None] = None,
    ) -> None:
        self.__id = device_id
        self.__identifier = device_identifier
        self.__name = device_name
        self.__state = device_state

        self.__controls = set(controls) if controls is not None else set()

        self.__last_communication_timestamp = None

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Device name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def state(self) -> ConnectionState:
        """Device connection state"""
        return self.__state

    # -----------------------------------------------------------------------------

    @state.setter
    def state(self, state: ConnectionState) -> None:
        """Device connection state setter"""
        self.__state = state

    # -----------------------------------------------------------------------------

    @property
    def controls(self) -> List[str]:
        """List of allowed device controls"""
        return list(self.__controls)

    # -----------------------------------------------------------------------------

    @property
    def last_communication_timestamp(self) -> Optional[float]:
        """Last device communication timestamp"""
        return self.__last_communication_timestamp

    # -----------------------------------------------------------------------------

    @last_communication_timestamp.setter
    def last_communication_timestamp(self, last_communication_timestamp: Optional[float]) -> None:
        """Set last device communication timestamp"""
        self.__last_communication_timestamp = last_communication_timestamp

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceRecord):
            return False

        return (
            self.id == other.id
            and self.identifier == other.identifier
            and self.name == other.name
            and self.controls == other.controls
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class DevicePropertyRecord:  # pylint: disable=too-many-instance-attributes
    """
    Device property record

    @package        FastyBird:FbMqttConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID

    __identifier: str
    __name: Optional[str]
    __value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None
    __unit: Optional[str]
    __data_type: DataType

    __queryable: bool = False
    __settable: bool = False

    __actual_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_pending: Optional[float] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str],
        property_data_type: DataType,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> None:
        self.__device_id = device_id

        self.__id = property_id
        self.__identifier = property_identifier
        self.__name = property_name
        self.__value_format = property_value_format
        self.__unit = property_unit
        self.__data_type = property_data_type

        self.__queryable = property_queryable
        self.__settable = property_settable

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Property device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Property unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Property unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Property name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Property optional value data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        """Property optional value format"""
        return self.__value_format

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Property value unit"""
        return self.__unit

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is Property queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is Property settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property actual value"""
        return normalize_value(
            data_type=self.data_type,
            value=self.__actual_value,
            value_format=self.format,
            value_invalid=None,
        )

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Set Property actual value"""
        self.__actual_value = value

        if value == self.expected_value:
            self.expected_value = None
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property expected value"""
        return normalize_value(
            data_type=self.data_type,
            value=self.__expected_value,
            value_format=self.format,
            value_invalid=None,
        )

    # -----------------------------------------------------------------------------

    @expected_value.setter
    def expected_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Set Property expected value"""
        self.__expected_value = value

        if value is not None:
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_pending(self) -> Optional[float]:
        """Property expected value pending status"""
        return self.__expected_pending

    # -----------------------------------------------------------------------------

    @expected_pending.setter
    def expected_pending(self, timestamp: Optional[float]) -> None:
        """Set Property expected value transmit timestamp"""
        self.__expected_pending = timestamp

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DevicePropertyRecord):
            return False

        return (
            self.device_id == other.device_id
            and self.id == other.id
            and self.identifier == other.identifier
            and self.data_type == other.data_type
            and self.format == other.format
            and self.settable == other.settable
            and self.queryable == other.queryable
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class DeviceAttributeRecord:
    """
    Device attribute record

    @package        FastyBird:FbMqttConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID

    __identifier: str
    __name: Optional[str]
    __value: Optional[str]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_identifier: str,
        attribute_name: Optional[str],
        attribute_value: Optional[str],
    ) -> None:
        self.__device_id = device_id

        self.__id = attribute_id
        self.__identifier = attribute_identifier
        self.__name = attribute_name
        self.__value = attribute_value

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Attribute device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Attribute unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Attribute unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Attribute name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Optional[str]:
        """Attribute value"""
        return self.__value

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceAttributeRecord):
            return False

        return self.device_id == other.device_id and self.id == other.id and self.identifier == other.identifier

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class ChannelRecord:
    """
    Device channel record

    @package        FastyBird:FbMqttConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID

    __identifier: str
    __name: Optional[str]

    __controls: Set[str] = set()

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        channel_id: uuid.UUID,
        channel_identifier: str,
        channel_name: Optional[str] = None,
        controls: Union[List[str], None] = None,
    ) -> None:
        self.__device_id = device_id

        self.__id = channel_id
        self.__identifier = channel_identifier
        self.__name = channel_name

        self.__controls = set(controls) if controls is not None else set()

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Channel device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Channel unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Channel unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Channel name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def controls(self) -> List[str]:
        """List of allowed channel controls"""
        return list(self.__controls)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChannelRecord):
            return False

        return (
            self.device_id == other.device_id
            and self.id == other.id
            and self.identifier == other.identifier
            and self.name == other.name
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class ChannelPropertyRecord:  # pylint: disable=too-many-instance-attributes
    """
    Channel property record

    @package        FastyBird:FbMqttConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __channel_id: uuid.UUID

    __id: uuid.UUID

    __identifier: str
    __name: Optional[str]
    __value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None
    __unit: Optional[str]
    __data_type: DataType

    __queryable: bool = False
    __settable: bool = False

    __actual_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_pending: Optional[float] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        channel_id: uuid.UUID,
        property_id: uuid.UUID,
        property_identifier: str,
        property_name: Optional[str],
        property_data_type: DataType,
        property_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        property_unit: Optional[str] = None,
        property_queryable: bool = False,
        property_settable: bool = False,
    ) -> None:
        self.__channel_id = channel_id

        self.__id = property_id
        self.__identifier = property_identifier
        self.__name = property_name
        self.__value_format = property_value_format
        self.__unit = property_unit
        self.__data_type = property_data_type

        self.__queryable = property_queryable
        self.__settable = property_settable

    # -----------------------------------------------------------------------------

    @property
    def channel_id(self) -> uuid.UUID:
        """Property channel unique identifier"""
        return self.__channel_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Property unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Property unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Property name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Property optional value data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        """Property optional value format"""
        return self.__value_format

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Property value unit"""
        return self.__unit

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is Property queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is Property settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property actual value"""
        return normalize_value(
            data_type=self.data_type,
            value=self.__actual_value,
            value_format=self.format,
            value_invalid=None,
        )

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Set Property actual value"""
        self.__actual_value = value

        if value == self.expected_value:
            self.expected_value = None
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property expected value"""
        return normalize_value(
            data_type=self.data_type,
            value=self.__expected_value,
            value_format=self.format,
            value_invalid=None,
        )

    # -----------------------------------------------------------------------------

    @expected_value.setter
    def expected_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Set Property expected value"""
        self.__expected_value = value

        if value is not None:
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_pending(self) -> Optional[float]:
        """Property expected value pending status"""
        return self.__expected_pending

    # -----------------------------------------------------------------------------

    @expected_pending.setter
    def expected_pending(self, timestamp: Optional[float]) -> None:
        """Set Property expected value transmit timestamp"""
        self.__expected_pending = timestamp

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChannelPropertyRecord):
            return False

        return (
            self.channel_id == other.channel_id
            and self.id == other.id
            and self.identifier == other.identifier
            and self.data_type == other.data_type
            and self.format == other.format
            and self.settable == other.settable
            and self.queryable == other.queryable
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()
