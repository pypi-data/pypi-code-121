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
Devices module channel repositories module
"""

# Python base dependencies
import uuid
from typing import List, Optional

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)


class ChannelsRepository:
    """
    Channels repository

    @package        FastyBird:DevicesModule!
    @module         repositories/channel

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

    def get_by_id(self, channel_id: uuid.UUID) -> Optional[ChannelEntity]:
        """Find channel by provided database identifier"""
        return self.__session.query(ChannelEntity).get(channel_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, device_id: uuid.UUID, channel_identifier: str) -> Optional[ChannelEntity]:
        """Find channel by provided identifier"""
        return (
            self.__session.query(ChannelEntity)
            .filter(ChannelEntity.device_id == device_id.bytes, ChannelEntity.col_identifier == channel_identifier)
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ChannelEntity]:
        """Find all channels"""
        return self.__session.query(ChannelEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[ChannelEntity]:
        """Find all channels for device"""
        return self.__session.query(ChannelEntity).filter(ChannelEntity.device_id == device_id.bytes).all()


class ChannelPropertiesRepository:
    """
    Channel property repository

    @package        FastyBird:DevicesModule!
    @module         repositories/channel

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

    def get_by_id(self, property_id: uuid.UUID) -> Optional[ChannelPropertyEntity]:
        """Find property by provided database identifier"""
        return self.__session.query(ChannelPropertyEntity).get(property_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_identifier(self, channel_id: uuid.UUID, property_identifier: str) -> Optional[ChannelPropertyEntity]:
        """Find property by provided identifier"""
        return (
            self.__session.query(ChannelPropertyEntity)
            .filter(
                ChannelPropertyEntity.channel_id == channel_id.bytes,
                ChannelPropertyEntity.col_identifier == property_identifier,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ChannelPropertyEntity]:
        """Find all channels properties"""
        return self.__session.query(ChannelPropertyEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_channel(self, channel_id: uuid.UUID) -> List[ChannelPropertyEntity]:
        """Find all channels properties for channel"""
        return (
            self.__session.query(ChannelPropertyEntity)
            .filter(ChannelPropertyEntity.channel_id == channel_id.bytes)
            .all()
        )

    # -----------------------------------------------------------------------------

    def get_all_by_parent(self, property_id: uuid.UUID) -> List[ChannelPropertyEntity]:
        """Find all child properties"""
        return (
            self.__session.query(ChannelPropertyEntity)
            .filter(ChannelPropertyEntity.parent_id == property_id.bytes)
            .all()
        )


class ChannelControlsRepository:
    """
    Channels controls repository

    @package        FastyBird:DevicesModule!
    @module         repositories/channel

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

    def get_by_id(self, control_id: uuid.UUID) -> Optional[ChannelControlEntity]:
        """Find control by provided database identifier"""
        return self.__session.query(ChannelControlEntity).get(control_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_name(self, channel_id: uuid.UUID, control_name: str) -> Optional[ChannelControlEntity]:
        """Find control by provided name"""
        return (
            self.__session.query(ChannelControlEntity)
            .filter(
                ChannelControlEntity.channel_id == channel_id.bytes,
                ChannelControlEntity.col_name == control_name,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ChannelControlEntity]:
        """Find all channels controls"""
        return self.__session.query(ChannelControlEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_channel(self, channel_id: uuid.UUID) -> List[ChannelControlEntity]:
        """Find all channels controls for channel"""
        return (
            self.__session.query(ChannelControlEntity).filter(ChannelControlEntity.channel_id == channel_id.bytes).all()
        )
