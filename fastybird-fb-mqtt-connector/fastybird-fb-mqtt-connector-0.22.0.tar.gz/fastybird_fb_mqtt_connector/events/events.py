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
FastyBird MQTT connector events module events
"""

# Python base dependencies
from typing import Optional

# Library dependencies
from whistle import Event

# Library libs
from fastybird_fb_mqtt_connector.registry.records import (
    ChannelPropertyRecord,
    ChannelRecord,
    DeviceAttributeRecord,
    DevicePropertyRecord,
    DeviceRecord,
)


class DeviceRecordUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device record was updated in registry

    @package        FastyBird:FbMqttConnector!
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


class ChannelRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Channel record was created or updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: ChannelRecord

    EVENT_NAME: str = "registry.channelRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: ChannelRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> ChannelRecord:
        """Created or updated channel record"""
        return self.__record


class ChannelRecordDeletedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Channel record was deleted from registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: ChannelRecord

    EVENT_NAME: str = "registry.channelRecordDeleted"

    # -----------------------------------------------------------------------------

    def __init__(self, record: ChannelRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> ChannelRecord:
        """Deleted channel record"""
        return self.__record


class DevicePropertyRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device property record was created or updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DevicePropertyRecord

    EVENT_NAME: str = "registry.devicePropertyRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DevicePropertyRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DevicePropertyRecord:
        """Created or updated property record"""
        return self.__record


class DevicePropertyRecordDeletedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device property record was deleted from registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DevicePropertyRecord

    EVENT_NAME: str = "registry.devicePropertyRecordDeleted"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DevicePropertyRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DevicePropertyRecord:
        """Deleted property record"""
        return self.__record


class DeviceAttributeRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device attribute record was created or updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DeviceAttributeRecord

    EVENT_NAME: str = "registry.deviceAttributeRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DeviceAttributeRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DeviceAttributeRecord:
        """Created or updated attribute record"""
        return self.__record


class DeviceAttributeRecordDeletedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device attribute record was deleted from registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DeviceAttributeRecord

    EVENT_NAME: str = "registry.deviceAttributeRecordDeleted"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DeviceAttributeRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DeviceAttributeRecord:
        """Deleted attribute record"""
        return self.__record


class ChannelPropertyRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Channel property record was created or updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: ChannelPropertyRecord

    EVENT_NAME: str = "registry.channelPropertyRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: ChannelPropertyRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> ChannelPropertyRecord:
        """Created or updated property record"""
        return self.__record


class ChannelPropertyRecordDeletedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Channel property record was deleted from registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: ChannelPropertyRecord

    EVENT_NAME: str = "registry.channelPropertyRecordDeleted"

    # -----------------------------------------------------------------------------

    def __init__(self, record: ChannelPropertyRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> ChannelPropertyRecord:
        """Deleted property record"""
        return self.__record


class DevicePropertyActualValueEvent(Event):
    """
    Device property record actual value was updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[DevicePropertyRecord]
    __updated_record: DevicePropertyRecord

    EVENT_NAME: str = "registry.devicePropertyRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[DevicePropertyRecord], updated_record: DevicePropertyRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[DevicePropertyRecord]:
        """Original property record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> DevicePropertyRecord:
        """Updated property record"""
        return self.__updated_record


class ChannelPropertyActualValueEvent(Event):
    """
    Channel property record actual value was updated in registry

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[ChannelPropertyRecord]
    __updated_record: ChannelPropertyRecord

    EVENT_NAME: str = "registry.channelPropertyRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[ChannelPropertyRecord], updated_record: ChannelPropertyRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[ChannelPropertyRecord]:
        """Original property record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> ChannelPropertyRecord:
        """Updated property record"""
        return self.__updated_record


class DeviceStateChangedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device state was changed

    @package        FastyBird:FbMqttConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DeviceRecord

    EVENT_NAME: str = "registry.deviceStateChanged"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DeviceRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DeviceRecord:
        """Changed device record"""
        return self.__record
