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
Tuya connector consumers module entities
"""

# Python base dependencies
import uuid
from abc import ABC
from typing import List, Optional, Set, Union


class BaseEntity(ABC):  # pylint: disable=too-few-public-methods
    """
    Base message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_identifier: str

    # -----------------------------------------------------------------------------

    def __init__(self, device_identifier: str) -> None:
        self.__device_identifier = device_identifier

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique identifier"""
        return self.__device_identifier


class DeviceFoundEntity(BaseEntity):  # pylint: disable=too-few-public-methods
    """
    New device found message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class CloudDeviceFoundEntity(DeviceFoundEntity):  # pylint: disable=too-few-public-methods
    """
    New cloud device found message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class LocalDeviceFoundEntity(DeviceFoundEntity):  # pylint: disable=too-few-public-methods
    """
    New local device found message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class DeviceStatusEntity(BaseEntity):
    """
    Device status message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __dps_states: Set["DpStatusEntity"] = set()

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_identifier: str,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
        )

        self.__dps_states = set()

    # -----------------------------------------------------------------------------

    @property
    def dps_states(self) -> List["DpStatusEntity"]:
        """All propagated device sensor&states statuses"""
        return list(self.__dps_states)

    # -----------------------------------------------------------------------------

    def add_dps_state(self, sensor: "DpStatusEntity") -> None:
        """Add sensor&state status"""
        self.__dps_states.add(sensor)


class DpStatusEntity:
    """
    Data point status message entity

    @package        FastyBird:TuyaConnector!
    @module         consumers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: Optional[uuid.UUID]
    __device_identifier: Optional[str]

    __index: Optional[int]
    __identifier: Optional[str]

    __value: Union[str, int, bool]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        dp_value: Union[str, int, bool],
        device_id: Optional[uuid.UUID] = None,
        device_identifier: Optional[str] = None,
        dp_index: Optional[int] = None,
        dp_identifier: Optional[str] = None,
    ) -> None:
        if device_id is None and device_identifier is None:
            raise Exception("Device ID or identifier have to be set")

        if dp_index is None and dp_identifier is None:
            raise Exception("Data point index or identifier have to be set")

        self.__device_id = device_id
        self.__device_identifier = device_identifier

        self.__index = dp_index
        self.__identifier = dp_identifier

        self.__value = dp_value

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> Optional[uuid.UUID]:
        """Device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def device_identifier(self) -> Optional[str]:
        """Device unique identifier"""
        return self.__device_identifier

    # -----------------------------------------------------------------------------

    @property
    def index(self) -> Optional[int]:
        """Data point index"""
        return self.__index

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> Optional[str]:
        """Data point code/identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[str, int, bool]:
        """Data point actual value"""
        return self.__value
