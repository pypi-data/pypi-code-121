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
Tuya connector registry module records
"""

# Python base dependencies
import uuid
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import DataType

# Library libs
from fastybird_tuya_connector.types import (
    DataPointType,
    DeviceAttribute,
    DeviceProperty,
    DeviceProtocolVersion,
)


class DeviceRecord:
    """
    Tuya device record

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID

    __identifier: str

    __name: Optional[str] = None

    __parent_id: Optional[uuid.UUID] = None

    __last_communication_timestamp: Optional[float] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_id: uuid.UUID,
        device_identifier: str,
        device_name: Optional[str] = None,
        parent_id: Optional[uuid.UUID] = None,
    ) -> None:
        self.__id = device_id
        self.__identifier = device_identifier
        self.__name = device_name

        self.__parent_id = parent_id

        self.__last_communication_timestamp = None

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique tuya identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Device unique name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str] = None) -> None:
        """Set device unique name"""
        self.__name = name

    # -----------------------------------------------------------------------------

    @property
    def parent_id(self) -> Optional[uuid.UUID]:
        """Device parent unique identifier"""
        return self.__parent_id

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

        return self.id == other.id and self.identifier == other.identifier and self.parent_id == other.parent_id

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class DataPointRecord:  # pylint: disable=too-many-instance-attributes
    """
    Device data point record

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID

    __identifier: Optional[str] = None
    __index: Optional[int] = None
    __type: DataPointType
    __name: Optional[str] = None
    __unit: Optional[str] = None
    __value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None
    __data_type: DataType

    __queryable: bool = False
    __settable: bool = False

    __actual_value: Union[str, int, bool, None] = None
    __expected_value: Union[str, int, bool, None] = None
    __expected_pending: Optional[float] = None
    __actual_value_valid: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        dp_id: uuid.UUID,
        dp_type: DataPointType,
        dp_data_type: DataType,
        dp_identifier: Optional[str] = None,
        dp_index: Optional[int] = None,
        dp_name: Optional[str] = None,
        dp_unit: Optional[str] = None,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> None:
        if dp_identifier is None and dp_index is None:
            raise Exception("Data point identifier or index have to be set")

        self.__device_id = device_id

        self.__id = dp_id
        self.__identifier = dp_identifier
        self.__index = dp_index
        self.__type = dp_type
        self.__name = dp_name
        self.__data_type = dp_data_type
        self.__unit = dp_unit
        self.__value_format = dp_value_format

        self.__queryable = dp_queryable
        self.__settable = dp_settable

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Data point device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Data point unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> Optional[str]:
        """Data point unique code"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def index(self) -> Optional[int]:
        """Data point unique index"""
        return self.__index

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DataPointType:
        """Data point type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Data point name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Data point optional value data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Data point unit"""
        return self.__unit

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
        """Data point optional value format"""
        return self.__value_format

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is data point queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is data point settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, bool, None]:
        """Data point actual value"""
        normalizer_value = normalize_value(
            data_type=self.data_type,
            value=self.__actual_value,
            value_format=self.format,
            value_invalid=None,
        )

        if isinstance(normalizer_value, (str, int, bool)):
            return normalizer_value

        return None

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, bool, None]) -> None:
        """Set data point actual value"""
        self.__actual_value = value

        if self.actual_value == self.expected_value:
            self.expected_value = None
            self.expected_pending = None

        if self.expected_value is None:
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_value(self) -> Union[str, int, bool, None]:
        """Data point expected value"""
        normalizer_value = normalize_value(
            data_type=self.data_type,
            value=self.__expected_value,
            value_format=self.format,
            value_invalid=None,
        )

        if isinstance(normalizer_value, (str, int, bool)):
            return normalizer_value

        return None

    # -----------------------------------------------------------------------------

    @expected_value.setter
    def expected_value(self, value: Union[str, int, bool, None]) -> None:
        """Set data point expected value"""
        self.__expected_value = value
        self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_pending(self) -> Optional[float]:
        """Data point expected value pending status"""
        return self.__expected_pending

    # -----------------------------------------------------------------------------

    @expected_pending.setter
    def expected_pending(self, timestamp: Optional[float]) -> None:
        """Set data point expected value transmit timestamp"""
        self.__expected_pending = timestamp

    # -----------------------------------------------------------------------------

    @property
    def actual_value_valid(self) -> bool:
        """Data point actual value reading status"""
        return self.__actual_value_valid

    # -----------------------------------------------------------------------------

    @actual_value_valid.setter
    def actual_value_valid(self, state: bool) -> None:
        """Data point actual value reading status setter"""
        self.__actual_value_valid = state

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataPointRecord):
            return False

        return (
            self.device_id == other.device_id
            and self.id == other.id
            and self.identifier == other.identifier
            and self.type == other.type
            and self.name == other.name
            and self.data_type == other.data_type
            and self.format == other.format
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class PropertyRecord:
    """
    Device property record

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID
    __type: DeviceProperty
    __value: Union[str, int, bool, None] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_id: uuid.UUID,
        property_id: uuid.UUID,
        property_type: DeviceProperty,
        property_value: Union[str, int, bool, None] = None,
    ) -> None:
        self.__device_id = device_id

        self.__id = property_id
        self.__type = property_type
        self.__value = property_value

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Attribute unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DeviceProperty:
        """Attribute type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[str, int, bool, None]:
        """Attribute value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Union[str, int, bool, None]) -> None:
        """Set property value"""
        self.__value = value

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, bool, None]:
        """Attribute value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, bool, None]) -> None:
        """Set property value"""
        self.__value = value

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> Optional[DataType]:
        """Attribute data type"""
        if self.type == DeviceProperty.STATE:
            return DataType.ENUM

        return DataType.STRING

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[List[str], Tuple[Optional[int], Optional[int]], Tuple[Optional[float], Optional[float]], None]:
        """Attribute format"""
        if self.type == DeviceProperty.STATE:
            return [
                ConnectionState.CONNECTED.value,
                ConnectionState.DISCONNECTED.value,
                ConnectionState.UNKNOWN.value,
            ]

        return None

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PropertyRecord):
            return False

        return (
            self.device_id == other.device_id
            and self.id == other.id
            and self.type == other.type
            and self.data_type == other.data_type
            and self.format == other.format
            and self.actual_value == other.actual_value
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class AttributeRecord:
    """
    Device attribute record

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID
    __type: DeviceAttribute
    __value: Union[int, str, None] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, str, None] = None,
    ) -> None:
        self.__device_id = device_id

        self.__id = attribute_id
        self.__type = attribute_type
        self.__value = attribute_value

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Attribute unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DeviceAttribute:
        """Attribute type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[int, str, None]:
        """Attribute value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Union[int, str, None]) -> None:
        """Set attribute value"""
        self.__value = value

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributeRecord):
            return False

        return self.device_id == other.device_id and self.id == other.id and self.type == other.type

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class DiscoveredDevice:
    """
    Discovered local Tuya device instance

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: str
    __ip_address: str
    __product_key: str
    __local_key: Optional[str] = None
    __encrypted: bool
    __version: DeviceProtocolVersion

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: str,
        device_ip_address: str,
        device_product_key: str,
        device_encrypted: bool,
        device_version: str,
        device_local_key: Optional[str] = None,
    ) -> None:
        self.__id = device_id
        self.__ip_address = device_ip_address
        self.__product_key = device_product_key
        self.__local_key = device_local_key
        self.__encrypted = device_encrypted
        self.__version = (
            DeviceProtocolVersion(device_version)
            if DeviceProtocolVersion.has_value(device_version)
            else DeviceProtocolVersion.V33
        )

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Device identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def ip_address(self) -> str:
        """Device local ip address"""
        return self.__ip_address

    # -----------------------------------------------------------------------------

    @property
    def product_key(self) -> str:
        """Device product key"""
        return self.__product_key

    # -----------------------------------------------------------------------------

    @property
    def local_key(self) -> Optional[str]:
        """Device local communication key"""
        return self.__local_key

    # -----------------------------------------------------------------------------

    @property
    def encrypted(self) -> bool:
        """Does device use encryption?"""
        return self.__encrypted

    # -----------------------------------------------------------------------------

    @property
    def version(self) -> DeviceProtocolVersion:
        """Device firmware version"""
        return self.__version


class DiscoveredDataPoint:  # pylint: disable=too-many-instance-attributes
    """
    Discovered local Tuya device data point instance

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: str

    __index: int
    __type: DataPointType
    __data_type: DataType

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: str,
        dp_index: int,
        dp_type: DataPointType,
        dp_data_type: DataType,
    ) -> None:
        self.__device_id = device_id

        self.__index = dp_index
        self.__type = dp_type
        self.__data_type = dp_data_type

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> str:
        """Data point device identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def index(self) -> int:
        """Data point local index"""
        return self.__index

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DataPointType:
        """Data point type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Data point data type"""
        return self.__data_type


class TuyaCloudDevice:  # pylint: disable=too-many-instance-attributes
    """
    Tuya cloud device instance

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: str
    __local_key: str
    __name: str
    __uid: str
    __model: str
    __serial_number: Optional[str] = None
    __mac_address: Optional[str] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: str,
        device_local_key: str,
        device_name: str,
        device_uid: str,
        device_model: str,
        device_serial_number: Optional[str] = None,
        device_mac_address: Optional[str] = None,
    ) -> None:
        self.__id = device_id
        self.__local_key = device_local_key
        self.__name = device_name
        self.__uid = device_uid
        self.__model = device_model
        self.__serial_number = device_serial_number
        self.__mac_address = device_mac_address

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Tuya device identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def local_key(self) -> str:
        """Device local key"""
        return self.__local_key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Device name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def uid(self) -> str:
        """Device user identifier"""
        return self.__uid

    # -----------------------------------------------------------------------------

    @property
    def model(self) -> str:
        """Device model name"""
        return self.__model

    # -----------------------------------------------------------------------------

    @property
    def serial_number(self) -> Optional[str]:
        """Device serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def mac_address(self) -> Optional[str]:
        """Device hardware mac address"""
        return self.__mac_address


class TuyaCloudDataPoint:  # pylint: disable=too-many-instance-attributes
    """
    Tuya cloud device data point instance

    @package        FastyBird:TuyaConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: str

    __code: str
    __type: DataPointType
    __name: str
    __data_type: DataType
    __value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None
    __unit: Optional[str] = None
    __min_value: Optional[int] = None
    __max_value: Optional[int] = None
    __step_value: Optional[int] = None
    __queryable: bool = False
    __settable: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: str,
        dp_code: str,
        dp_type: DataPointType,
        dp_name: str,
        dp_data_type: DataType,
        dp_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        dp_unit: Optional[str] = None,
        dp_min_value: Optional[int] = None,
        dp_max_value: Optional[int] = None,
        dp_step_value: Optional[int] = None,
        dp_queryable: bool = False,
        dp_settable: bool = False,
    ) -> None:
        self.__device_id = device_id

        self.__code = dp_code
        self.__type = dp_type
        self.__name = dp_name
        self.__data_type = dp_data_type
        self.__value_format = dp_value_format
        self.__unit = dp_unit
        self.__min_value = dp_min_value
        self.__max_value = dp_max_value
        self.__step_value = dp_step_value
        self.__queryable = dp_queryable
        self.__settable = dp_settable

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> str:
        """Data point device identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def code(self) -> str:
        """Data point code"""
        return self.__code

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DataPointType:
        """Data point type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Data point name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Data point data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def value_format(
        self,
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        """Data point value format"""
        return self.__value_format

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Data point unit"""
        return self.__unit

    # -----------------------------------------------------------------------------

    @property
    def min_value(self) -> Optional[int]:
        """Data point minimal value"""
        return self.__min_value

    # -----------------------------------------------------------------------------

    @property
    def max_value(self) -> Optional[int]:
        """Data point maximal value"""
        return self.__max_value

    # -----------------------------------------------------------------------------

    @property
    def step_value(self) -> Optional[int]:
        """Data point step value"""
        return self.__step_value

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is data point queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is data point settable?"""
        return self.__settable
