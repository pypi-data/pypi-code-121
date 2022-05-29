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
Shelly connector events module events
"""

# Python base dependencies
from typing import Optional

# Library dependencies
from whistle import Event

# Library libs
from fastybird_shelly_connector.registry.records import (
    BlockRecord,
    DeviceRecord,
    PropertyRecord,
    SensorRecord,
)


class DeviceRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device record was created or updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DeviceRecord

    EVENT_NAME: str = "registry.deviceRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DeviceRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DeviceRecord:
        """Created or updated device record"""
        return self.__record


class BlockRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's block record was created or updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: BlockRecord

    EVENT_NAME: str = "registry.blockRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: BlockRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> BlockRecord:
        """Created or updated block record"""
        return self.__record


class SensorRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Block's sensor record was created or updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: SensorRecord

    EVENT_NAME: str = "registry.sensorRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: SensorRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> SensorRecord:
        """Created or updated sensor record"""
        return self.__record


class PropertyRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's property record was created or updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: PropertyRecord

    EVENT_NAME: str = "registry.propertyRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: PropertyRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> PropertyRecord:
        """Created or updated property record"""
        return self.__record


class PropertyActualValueEvent(Event):
    """
    Property record actual value was updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[PropertyRecord]
    __updated_record: PropertyRecord

    EVENT_NAME: str = "registry.propertyRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[PropertyRecord], updated_record: PropertyRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[PropertyRecord]:
        """Original property record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> PropertyRecord:
        """Updated property record"""
        return self.__updated_record


class SensorActualValueEvent(Event):
    """
    Sensor&State record actual value was updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[SensorRecord]
    __updated_record: SensorRecord

    EVENT_NAME: str = "registry.sensorRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[SensorRecord], updated_record: SensorRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[SensorRecord]:
        """Original sensor&state record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> SensorRecord:
        """Updated sensor&state record"""
        return self.__updated_record
