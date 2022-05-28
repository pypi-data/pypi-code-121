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
FastyBird BUS connector registry module records
"""

# pylint: disable=too-many-lines

# Python base dependencies
import time
import uuid
from abc import ABC
from datetime import datetime
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_devices_module.utils import normalize_value
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload

# Library libs
from fastybird_fb_bus_connector.types import DeviceProperty, Packet, RegisterType


class DeviceRecord:  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """
    Device record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID
    __serial_number: str

    __enabled: bool = False

    __last_writing_packet_timestamp: float = 0.0  # Timestamp writing when request was sent to the device
    __last_reading_packet_timestamp: float = 0.0  # Timestamp reading when request was sent to the device
    __last_misc_packet_timestamp: float = 0.0  # Timestamp reading misc when request was sent to the device

    __attempts: int = 0

    __sampling_time: float = 10.0

    __lost_timestamp: float = 0.0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_id: uuid.UUID,
        serial_number: str,
        enabled: bool = False,
    ) -> None:
        self.__id = device_id
        self.__serial_number = serial_number
        self.__enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def serial_number(self) -> str:
        """Device unique serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Is device enabled?"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Enable or disable device"""
        self.__enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def last_reading_packet_timestamp(self) -> float:
        """Last reading packet sent time stamp"""
        return self.__last_reading_packet_timestamp

    # -----------------------------------------------------------------------------

    @last_reading_packet_timestamp.setter
    def last_reading_packet_timestamp(self, timestamp: float) -> None:
        """Last reading packet sent time stamp setter"""
        self.__last_reading_packet_timestamp = timestamp

    # -----------------------------------------------------------------------------

    @property
    def last_writing_packet_timestamp(self) -> float:
        """Last writing packet sent time stamp"""
        return self.__last_writing_packet_timestamp

    # -----------------------------------------------------------------------------

    @last_writing_packet_timestamp.setter
    def last_writing_packet_timestamp(self, timestamp: float) -> None:
        """Last writing packet sent time stamp setter"""
        self.__last_writing_packet_timestamp = timestamp

    # -----------------------------------------------------------------------------

    @property
    def last_misc_packet_timestamp(self) -> float:
        """Last misc packet sent time stamp"""
        return self.__last_misc_packet_timestamp

    # -----------------------------------------------------------------------------

    @last_misc_packet_timestamp.setter
    def last_misc_packet_timestamp(self, timestamp: float) -> None:
        """Last misc packet sent time stamp setter"""
        self.__last_misc_packet_timestamp = timestamp

    # -----------------------------------------------------------------------------

    @property
    def transmit_attempts(self) -> int:
        """Transmit packet attempts count"""
        return self.__attempts

    # -----------------------------------------------------------------------------

    @transmit_attempts.setter
    def transmit_attempts(self, attempts: int) -> None:
        """Transmit packet attempts count setter"""
        self.__attempts = attempts

    # -----------------------------------------------------------------------------

    @property
    def lost_timestamp(self) -> float:
        """Time stamp when communication with device was lost"""
        return self.__lost_timestamp

    # -----------------------------------------------------------------------------

    @lost_timestamp.setter
    def lost_timestamp(self, timestamp: float) -> None:
        """Set lost communication time stamp"""
        self.__lost_timestamp = timestamp

    # -----------------------------------------------------------------------------

    @property
    def is_lost(self) -> bool:
        """Is device in lost state?"""
        return self.__lost_timestamp != 0

    # -----------------------------------------------------------------------------

    @property
    def sampling_time(self) -> float:
        """Device registers reading sampling time"""
        return self.__sampling_time

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class RegisterRecord(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Base register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID
    __address: int
    __type: RegisterType
    __data_type: DataType
    __invalid: Union[int, float, str, None] = None
    __settable: bool = False
    __queryable: bool = False

    _actual_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    _expected_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    _expected_pending: Optional[float] = None
    _actual_value_valid: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        self.__device_id = device_id

        self.__id = register_id
        self.__address = register_address
        self.__type = register_type
        self.__data_type = register_data_type
        self.__invalid = register_invalid
        self.__settable = register_settable
        self.__queryable = register_queryable

        self._actual_value = None
        self._expected_value = None
        self._expected_pending = False

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Device unique database identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Register unique database identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Register address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Record data type"""
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
        """Register value format"""
        if self.data_type == DataType.SWITCH:
            return [
                SwitchPayload.ON.value,
                SwitchPayload.OFF.value,
                SwitchPayload.TOGGLE.value,
            ]

        if self.data_type == DataType.BUTTON:
            return [
                ButtonPayload.PRESSED.value,
                ButtonPayload.RELEASED.value,
                ButtonPayload.CLICKED.value,
                ButtonPayload.DOUBLE_CLICKED.value,
                ButtonPayload.TRIPLE_CLICKED.value,
                ButtonPayload.LONG_CLICKED.value,
                ButtonPayload.EXTRA_LONG_CLICKED.value,
            ]

        return None

    # -----------------------------------------------------------------------------

    @property
    def invalid(self) -> Union[int, float, str, None]:
        """Invalid value representation"""
        return self.__invalid

    # -----------------------------------------------------------------------------

    @property
    def data_type_size(self) -> int:
        """Register data type bytes size"""
        if self.data_type in (
            DataType.UCHAR,
            DataType.CHAR,
            DataType.BUTTON,
            DataType.SWITCH,
        ):
            return 1

        if self.data_type in (
            DataType.USHORT,
            DataType.SHORT,
        ):
            return 2

        if self.data_type in (
            DataType.UINT,
            DataType.INT,
            DataType.FLOAT,
        ):
            return 4

        if self.data_type == DataType.BOOLEAN:
            return 2

        return 0

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is register settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is register queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Register actual value"""
        return normalize_value(
            data_type=self.data_type,
            value=self._actual_value,
            value_format=self.format,
            value_invalid=self.invalid,
        )

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Register actual value setter"""
        self._actual_value = value

        if self.actual_value == self.expected_value and self.expected_value is not None:
            self.expected_value = None
            self.expected_pending = None

        if self.expected_value is None:
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Register expected value"""
        return normalize_value(
            data_type=self.data_type,
            value=self._expected_value,
            value_format=self.format,
            value_invalid=self.invalid,
        )

    # -----------------------------------------------------------------------------

    @expected_value.setter
    def expected_value(
        self,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        """Register expected value setter"""
        self._expected_value = value
        self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_pending(self) -> Optional[float]:
        """Register expected value pending status"""
        return self._expected_pending

    # -----------------------------------------------------------------------------

    @expected_pending.setter
    def expected_pending(self, timestamp: Optional[float]) -> None:
        """Register expected value transmit timestamp setter"""
        self._expected_pending = timestamp

    # -----------------------------------------------------------------------------

    @property
    def actual_value_valid(self) -> bool:
        """Register actual value reading status"""
        return self._actual_value_valid

    # -----------------------------------------------------------------------------

    @actual_value_valid.setter
    def actual_value_valid(self, state: bool) -> None:
        """Register actual value reading status setter"""
        self._actual_value_valid = state

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class InputRegisterRecord(RegisterRecord):
    """
    Input register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __channel_id: Optional[uuid.UUID] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.INPUT,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            register_settable=False,
            register_queryable=True,
        )

        self.__channel_id = channel_id

    # -----------------------------------------------------------------------------

    @property
    def channel_id(self) -> Optional[uuid.UUID]:
        """Device channel unique database identifier"""
        return self.__channel_id


class OutputRegisterRecord(RegisterRecord):
    """
    Output register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __channel_id: Optional[uuid.UUID] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_invalid: Union[int, float, str, None] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.OUTPUT,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            register_settable=True,
            register_queryable=True,
        )

        self.__channel_id = channel_id

    # -----------------------------------------------------------------------------

    @property
    def channel_id(self) -> Optional[uuid.UUID]:
        """Device channel unique database identifier"""
        return self.__channel_id


class AttributeRegisterRecord(RegisterRecord):
    """
    Attribute register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __name: Optional[str] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
        register_invalid: Union[int, float, str, None] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.ATTRIBUTE,
            register_data_type=register_data_type,
            register_invalid=register_invalid,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )

        self.__name = register_name

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Attribute register name"""
        return self.__name

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
        """Attribute register value format"""
        if self.name == DeviceProperty.STATE.value:
            return [
                ConnectionState.RUNNING.value,
                ConnectionState.STOPPED.value,
                ConnectionState.DISCONNECTED.value,
                ConnectionState.LOST.value,
                ConnectionState.ALERT.value,
                ConnectionState.UNKNOWN.value,
            ]

        return super().format


class DeviceAttributeRecord:
    """
    Device attribute record

    @package        FastyBird:FbBusConnector!
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


class DiscoveredDeviceRecord:  # pylint: disable=too-many-instance-attributes
    """
    Discovered device record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __address: int
    __serial_number: str
    __state: ConnectionState

    __max_packet_length: int

    __hardware_version: str
    __hardware_model: str
    __hardware_manufacturer: str

    __firmware_version: str
    __firmware_manufacturer: str

    __input_registers_size: int
    __output_registers_size: int
    __attributes_registers_size: int

    __waiting_for_packet: Optional[Packet] = None
    __last_packet_sent_timestamp: float = 0.0  # Timestamp when request was sent to the device

    __attempts: int = 0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_address: int,
        device_max_packet_length: int,
        device_serial_number: str,
        device_state: ConnectionState,
        device_hardware_version: str,
        device_hardware_model: str,
        device_hardware_manufacturer: str,
        device_firmware_version: str,
        device_firmware_manufacturer: str,
        input_registers_size: int,
        output_registers_size: int,
        attributes_registers_size: int,
    ) -> None:
        self.__address = device_address
        self.__max_packet_length = device_max_packet_length
        self.__serial_number = device_serial_number
        self.__state = device_state

        self.__hardware_version = device_hardware_version
        self.__hardware_model = device_hardware_model
        self.__hardware_manufacturer = device_hardware_manufacturer

        self.__firmware_version = device_firmware_version
        self.__firmware_manufacturer = device_firmware_manufacturer

        self.__input_registers_size = input_registers_size
        self.__output_registers_size = output_registers_size
        self.__attributes_registers_size = attributes_registers_size

        self.__waiting_for_packet = None
        self.__last_packet_sent_timestamp = 0.0

        self.__attempts = 0

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Device communication address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @address.setter
    def address(self, address: int) -> None:
        """Set device communication address"""
        self.__address = address

    # -----------------------------------------------------------------------------

    @property
    def max_packet_length(self) -> int:
        """Maximum packet bytes length"""
        return self.__max_packet_length

    # -----------------------------------------------------------------------------

    @property
    def serial_number(self) -> str:
        """Serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def state(self) -> ConnectionState:
        """Actual state"""
        return self.__state

    # -----------------------------------------------------------------------------

    @property
    def hardware_version(self) -> str:
        """Hardware version number"""
        return self.__hardware_version

    # -----------------------------------------------------------------------------

    @property
    def hardware_model(self) -> str:
        """Hardware model"""
        return self.__hardware_model

    # -----------------------------------------------------------------------------

    @property
    def hardware_manufacturer(self) -> str:
        """Hardware manufacturer"""
        return self.__hardware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def firmware_version(self) -> str:
        """Firmware version number"""
        return self.__firmware_version

    # -----------------------------------------------------------------------------

    @property
    def firmware_manufacturer(self) -> str:
        """Firmware manufacturer"""
        return self.__firmware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def input_registers_size(self) -> int:
        """Input registers size"""
        return self.__input_registers_size

    # -----------------------------------------------------------------------------

    @property
    def output_registers_size(self) -> int:
        """Output registers size"""
        return self.__output_registers_size

    # -----------------------------------------------------------------------------

    @property
    def attributes_registers_size(self) -> int:
        """Attributes registers size"""
        return self.__attributes_registers_size

    # -----------------------------------------------------------------------------

    @property
    def last_packet_timestamp(self) -> float:
        """Last packet sent time stamp"""
        return self.__last_packet_sent_timestamp

    # -----------------------------------------------------------------------------

    @last_packet_timestamp.setter
    def last_packet_timestamp(self, last_packet_timestamp: float) -> None:
        """Last packet sent time stamp setter"""
        self.__last_packet_sent_timestamp = last_packet_timestamp

    # -----------------------------------------------------------------------------

    @property
    def waiting_for_packet(self) -> Optional[Packet]:
        """Packet identifier connector is waiting for"""
        return self.__waiting_for_packet

    # -----------------------------------------------------------------------------

    @waiting_for_packet.setter
    def waiting_for_packet(self, waiting_for_packet: Optional[Packet]) -> None:
        """Packet identifier connector is waiting for setter"""
        self.__waiting_for_packet = waiting_for_packet

        if waiting_for_packet is not None:
            self.__last_packet_sent_timestamp = time.time()
            self.__attempts = self.__attempts + 1

        else:
            self.__attempts = 0

    # -----------------------------------------------------------------------------

    @property
    def transmit_attempts(self) -> int:
        """Transmit packet attempts count"""
        return self.__attempts

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DiscoveredDeviceRecord):
            return False

        return self.serial_number == other.serial_number

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self.__serial_number)


class DiscoveredRegisterRecord(ABC):
    """
    Pairing base register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_address: int
    __device_serial_number: str

    __address: int
    __type: RegisterType
    __data_type: DataType
    __settable: bool = False
    __queryable: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_address: int,
        device_serial_number: str,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        self.__device_address = device_address
        self.__device_serial_number = device_serial_number

        self.__address = register_address
        self.__type = register_type
        self.__data_type = register_data_type

        self.__queryable = register_queryable
        self.__settable = register_settable

    # -----------------------------------------------------------------------------

    @property
    def device_serial_number(self) -> str:
        """Device serial number"""
        return self.__device_serial_number

    # -----------------------------------------------------------------------------

    @property
    def device_address(self) -> int:
        """Device communication address"""
        return self.__device_address

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Register address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Register data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is register settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is register queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DiscoveredRegisterRecord):
            return False

        return (
            self.device_serial_number == other.device_serial_number
            and self.device_address == other.device_address
            and self.address == other.address
            and self.type == other.type
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash((self.device_serial_number, self.device_address, self.address, self.type.value))


class DiscoveredInputRegisterRecord(DiscoveredRegisterRecord):
    """
    Pairing input register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(
        self,
        device_address: int,
        device_serial_number: str,
        register_address: int,
        register_data_type: DataType,
    ):
        super().__init__(
            device_address=device_address,
            device_serial_number=device_serial_number,
            register_address=register_address,
            register_type=RegisterType.INPUT,
            register_data_type=register_data_type,
            register_queryable=True,
            register_settable=False,
        )


class DiscoveredOutputRegisterRecord(DiscoveredRegisterRecord):
    """
    Pairing output register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(
        self,
        device_address: int,
        device_serial_number: str,
        register_address: int,
        register_data_type: DataType,
    ):
        super().__init__(
            device_address=device_address,
            device_serial_number=device_serial_number,
            register_address=register_address,
            register_type=RegisterType.OUTPUT,
            register_data_type=register_data_type,
            register_queryable=True,
            register_settable=True,
        )


class DiscoveredAttributeRegisterRecord(DiscoveredRegisterRecord):
    """
    Pairing attribute register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __name: Optional[str]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-branches,too-many-arguments
        self,
        device_address: int,
        device_serial_number: str,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
        register_settable: bool = False,
        register_queryable: bool = False,
    ):
        super().__init__(
            device_address=device_address,
            device_serial_number=device_serial_number,
            register_address=register_address,
            register_type=RegisterType.ATTRIBUTE,
            register_data_type=register_data_type,
            register_queryable=register_settable,
            register_settable=register_queryable,
        )

        self.__name = register_name

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Attribute register name"""
        return self.__name
