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
FastyBird BUS connector api module builder for API v1
"""

# Python base dependencies
from datetime import datetime
from typing import List, Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload

from fastybird_fb_bus_connector.api.transformers import (
    StateTransformHelpers,
    ValueTransformHelpers,
)

# Library libs
from fastybird_fb_bus_connector.exceptions import BuildPayloadException
from fastybird_fb_bus_connector.types import (
    DeviceProperty,
    Packet,
    ProtocolVersion,
    RegisterType,
)


class V1Builder:
    """
    BUS payload builder

    @package        FastyBird:FbBusConnector!
    @module         api/v1builder

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def build_ping(serial_number: Optional[str] = None) -> List[int]:
        """Build payload for device ping&pong"""
        return V1Builder.build_packet_preambule(packet=Packet.PING, serial_number=serial_number)

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_discovery() -> List[int]:
        """Build payload for device discover"""
        return V1Builder.build_packet_preambule(packet=Packet.DISCOVER)

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_read_single_register_value(
        register_type: RegisterType,
        register_address: int,
        serial_number: Optional[str] = None,
    ) -> List[int]:
        """Build payload for single register value reading"""
        output_content = V1Builder.build_packet_preambule(
            packet=Packet.READ_SINGLE_REGISTER_VALUE,
            serial_number=serial_number,
        )

        output_content.append(register_type.value)
        output_content.append(register_address >> 8)
        output_content.append(register_address & 0xFF)

        return output_content

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_read_multiple_registers_values(
        register_type: RegisterType,
        start_address: int,
        registers_count: int,
        serial_number: Optional[str] = None,
    ) -> List[int]:
        """Build payload for multiple registers values reading"""
        output_content = V1Builder.build_packet_preambule(
            packet=Packet.READ_MULTIPLE_REGISTERS_VALUES,
            serial_number=serial_number,
        )

        output_content.append(register_type.value)
        output_content.append(start_address >> 8)
        output_content.append(start_address & 0xFF)
        output_content.append(registers_count >> 8)
        output_content.append(registers_count & 0xFF)

        return output_content

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_read_single_register_structure(
        register_type: RegisterType,
        register_address: int,
        serial_number: Optional[str] = None,
    ) -> List[int]:
        """Build payload for single register structure reading"""
        output_content = V1Builder.build_packet_preambule(
            packet=Packet.READ_SINGLE_REGISTER_STRUCTURE,
            serial_number=serial_number,
        )

        output_content.append(register_type.value)
        output_content.append(register_address >> 8)
        output_content.append(register_address & 0xFF)

        return output_content

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_write_single_register_value(  # pylint: disable=too-many-arguments
        register_type: RegisterType,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
        write_value: Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime],
        serial_number: Optional[str] = None,
    ) -> List[int]:
        """Build payload for single register value writing"""
        output_content = V1Builder.build_packet_preambule(
            packet=Packet.WRITE_SINGLE_REGISTER_VALUE,
            serial_number=serial_number,
        )

        output_content.append(register_type.value)
        output_content.append(register_address >> 8)
        output_content.append(register_address & 0xFF)

        if register_data_type in (
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
            DataType.FLOAT,
            DataType.BOOLEAN,
        ) and isinstance(write_value, (int, float, bool)):
            transformed_value = ValueTransformHelpers.transform_to_bytes(
                data_type=register_data_type,
                value=write_value,
            )

            # Value could not be transformed
            if transformed_value is None:
                raise BuildPayloadException("Value to be written into register could not be transformed")

            for value in transformed_value:
                output_content.append(value)

        elif register_data_type in (
            DataType.BUTTON,
            DataType.SWITCH,
        ) and isinstance(write_value, (SwitchPayload, ButtonPayload)):
            transformed_value = ValueTransformHelpers.transform_to_bytes(
                data_type=register_data_type,
                value=write_value,
            )

            # Value could not be transformed
            if transformed_value is None:
                raise BuildPayloadException("Value to be written into register could not be transformed")

            for value in transformed_value:
                output_content.append(value)

        # SPECIAL TRANSFORMING FOR STATE ATTRIBUTE
        elif (
                register_data_type == DataType.ENUM
                and register_type == RegisterType.ATTRIBUTE
                and register_name == DeviceProperty.STATE.value
        ):
            transformed_value = ValueTransformHelpers.transform_to_bytes(
                data_type=DataType.UCHAR,
                value=StateTransformHelpers.transform_to_device(device_state=ConnectionState(write_value)).value,
            )

            # Value could not be transformed
            if transformed_value is None:
                raise BuildPayloadException("Value to be written into register could not be transformed")

            for value in transformed_value:
                output_content.append(value)

        else:
            raise BuildPayloadException("Unsupported register data type")

        return output_content

    # -----------------------------------------------------------------------------

    @staticmethod
    def build_packet_preambule(
        packet: Packet,
        serial_number: Optional[str] = None,
    ) -> List[int]:
        """Build packet preambule which is same for all packets"""
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            packet.value,
        ]

        if serial_number is not None:
            output_content.append(len(serial_number))

            for char in serial_number:
                output_content.append(ord(char))

        return output_content
