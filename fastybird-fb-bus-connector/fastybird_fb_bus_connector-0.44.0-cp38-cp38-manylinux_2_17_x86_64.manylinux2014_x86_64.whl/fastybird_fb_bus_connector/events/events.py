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
FastyBird BUS connector events module events
"""

# Python base dependencies
from typing import Optional, Union

# Library dependencies
from whistle import Event

# Library libs
from fastybird_fb_bus_connector.registry.records import (
    AttributeRegisterRecord,
    DeviceAttributeRecord,
    DeviceRecord,
    InputRegisterRecord,
    OutputRegisterRecord,
    RegisterRecord,
)


class DeviceRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device record was created or updated in registry

    @package        FastyBird:FbBusConnector!
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


class InputOutputRegisterRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device input or output register was created or updated in registry

    @package        FastyBird:FbBusConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: Union[InputRegisterRecord, OutputRegisterRecord]

    EVENT_NAME: str = "registry.inputOutputRegisterRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: Union[InputRegisterRecord, OutputRegisterRecord]) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> Union[InputRegisterRecord, OutputRegisterRecord]:
        """Created or updated register record"""
        return self.__record


class AttributeRegisterRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device attribute register was created or updated in registry

    @package        FastyBird:FbBusConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: AttributeRegisterRecord

    EVENT_NAME: str = "registry.attributeRegisterRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: AttributeRegisterRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> AttributeRegisterRecord:
        """Created or updated register record"""
        return self.__record


class DeviceAttributeRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device attribute record was created or updated in registry

    @package        FastyBird:FbBusConnector!
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

    @package        FastyBird:FbBusConnector!
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


class RegisterActualValueEvent(Event):
    """
    Register record actual value was updated in registry

    @package        FastyBird:FbBusConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[RegisterRecord]
    __updated_record: RegisterRecord

    EVENT_NAME: str = "registry.registerRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[RegisterRecord], updated_record: RegisterRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[RegisterRecord]:
        """Original register record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> RegisterRecord:
        """Updated register record"""
        return self.__updated_record
