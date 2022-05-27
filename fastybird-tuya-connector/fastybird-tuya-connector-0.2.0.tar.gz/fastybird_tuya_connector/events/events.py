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
Tuya connector events module events
"""

# Python base dependencies
from typing import Optional

# Library dependencies
from whistle import Event

# Library libs
from fastybird_tuya_connector.registry.records import (
    AttributeRecord,
    DataPointRecord,
    DeviceRecord,
    PropertyRecord,
)


class DeviceRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device record was created or updated in registry

    @package        FastyBird:TuyaConnector!
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


class DataPointRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's data point record was created or updated in registry

    @package        FastyBird:TuyaConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DataPointRecord

    EVENT_NAME: str = "registry.dataPointRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DataPointRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DataPointRecord:
        """Created or updated data point record"""
        return self.__record


class DevicePropertyRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's property record was created or updated in registry

    @package        FastyBird:TuyaConnector!
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


class DeviceAttributeRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's attribute record was created or updated in registry

    @package        FastyBird:TuyaConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: AttributeRecord

    EVENT_NAME: str = "registry.attributeRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: AttributeRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> AttributeRecord:
        """Created or updated attribute record"""
        return self.__record


class DataPointActualValueEvent(Event):
    """
    Data point record actual value was updated in registry

    @package        FastyBird:TuyaConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[DataPointRecord]
    __updated_record: DataPointRecord

    EVENT_NAME: str = "registry.dataPointRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[DataPointRecord], updated_record: DataPointRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[DataPointRecord]:
        """Original data point record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> DataPointRecord:
        """Updated data point record"""
        return self.__updated_record


class PropertyActualValueEvent(Event):
    """
    Property record actual value was updated in registry

    @package        FastyBird:TuyaConnector!
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


class AttributeActualValueEvent(Event):
    """
    Attribute record actual value was updated in registry

    @package        FastyBird:TuyaConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[AttributeRecord]
    __updated_record: AttributeRecord

    EVENT_NAME: str = "registry.attributeRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[AttributeRecord], updated_record: AttributeRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[AttributeRecord]:
        """Original attribute record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> AttributeRecord:
        """Updated attribute record"""
        return self.__updated_record
