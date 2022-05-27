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

# pylint: disable=comparison-with-callable

"""
Devices module device repositories module
"""

# Python base dependencies
import uuid
from typing import List, Optional

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.device import (
    DeviceAttributeEntity,
    DeviceControlEntity,
    DeviceEntity,
    DevicePropertyEntity,
)


class DevicesRepository:
    """
    Devices repository

    @package        FastyBird:DevicesModule!
    @module         repositories/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self.__session = session

    # -----------------------------------------------------------------------------

    def get_by_id(self, device_id: uuid.UUID) -> Optional[DeviceEntity]:
        """Find device by provided database identifier"""
        return self.__session.query(DeviceEntity).get(device_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, connector_id: uuid.UUID, device_identifier: str) -> Optional[DeviceEntity]:
        """Find device by provided identifier"""
        return (
            self.__session.query(DeviceEntity)
            .filter(
                DeviceEntity.connector_id == connector_id.bytes,
                DeviceEntity.col_identifier == device_identifier,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[DeviceEntity]:
        """Find all devices"""
        return self.__session.query(DeviceEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_parent(self, device_id: uuid.UUID) -> List[DeviceEntity]:
        """Find all devices for parent device"""
        return (
            self.__session.query(DeviceEntity)
            .filter(DeviceEntity.parent is not None, DeviceEntity.parent_id == device_id.bytes)
            .all()
        )

    # -----------------------------------------------------------------------------

    def get_all_by_connector(self, connector_id: uuid.UUID) -> List[DeviceEntity]:
        """Find all devices for connector"""
        return self.__session.query(DeviceEntity).filter(DeviceEntity.connector_id == connector_id.bytes).all()


class DevicePropertiesRepository:
    """
    Devices properties repository

    @package        FastyBird:DevicesModule!
    @module         repositories/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self.__session = session

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[DevicePropertyEntity]:
        """Find property by provided database identifier"""
        return self.__session.query(DevicePropertyEntity).get(property_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, property_identifier: str) -> Optional[DevicePropertyEntity]:
        """Find property by provided identifier"""
        return (
            self.__session.query(DevicePropertyEntity)
            .filter(
                DevicePropertyEntity.device_id == device_id.bytes,
                DevicePropertyEntity.col_identifier == property_identifier,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[DevicePropertyEntity]:
        """Find all devices properties"""
        return self.__session.query(DevicePropertyEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[DevicePropertyEntity]:
        """Find all devices properties for device"""
        return (
            self.__session.query(DevicePropertyEntity).filter(DevicePropertyEntity.device_id == device_id.bytes).all()
        )

    # -----------------------------------------------------------------------------

    def get_all_by_parent(self, property_id: uuid.UUID) -> List[DevicePropertyEntity]:
        """Find all child properties"""
        return (
            self.__session.query(DevicePropertyEntity).filter(DevicePropertyEntity.parent_id == property_id.bytes).all()
        )


class DeviceControlsRepository:
    """
    Devices controls repository

    @package        FastyBird:DevicesModule!
    @module         repositories/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self.__session = session

    # -----------------------------------------------------------------------------

    def get_by_id(self, control_id: uuid.UUID) -> Optional[DeviceControlEntity]:
        """Find control by provided database identifier"""
        return self.__session.query(DeviceControlEntity).get(control_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_name(self, device_id: uuid.UUID, control_name: str) -> Optional[DeviceControlEntity]:
        """Find control by provided name"""
        return (
            self.__session.query(DeviceControlEntity)
            .filter(DeviceControlEntity.device_id == device_id.bytes, DeviceControlEntity.col_name == control_name)
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[DeviceControlEntity]:
        """Find all devices controls"""
        return self.__session.query(DeviceControlEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[DeviceControlEntity]:
        """Find all devices controls for device"""
        return self.__session.query(DeviceControlEntity).filter(DeviceControlEntity.device_id == device_id.bytes).all()


class DeviceAttributesRepository:
    """
    Devices attributes repository

    @package        FastyBird:DevicesModule!
    @module         repositories/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self.__session = session

    # -----------------------------------------------------------------------------

    def get_by_id(self, attribute_id: uuid.UUID) -> Optional[DeviceAttributeEntity]:
        """Find attribute by provided database identifier"""
        return self.__session.query(DeviceAttributeEntity).get(attribute_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, attribute_identifier: str) -> Optional[DeviceAttributeEntity]:
        """Find attribute by provided name"""
        return (
            self.__session.query(DeviceAttributeEntity)
            .filter(
                DeviceAttributeEntity.device_id == device_id.bytes,
                DeviceAttributeEntity.col_identifier == attribute_identifier,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[DeviceAttributeEntity]:
        """Find all devices attributes"""
        return self.__session.query(DeviceAttributeEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[DeviceAttributeEntity]:
        """Find all devices attributes for device"""
        return (
            self.__session.query(DeviceAttributeEntity).filter(DeviceAttributeEntity.device_id == device_id.bytes).all()
        )
