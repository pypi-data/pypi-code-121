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
Devices module state repositories module
"""

# Python base dependencies
import uuid
from abc import ABC, abstractmethod
from typing import Optional

# Library dependencies
from kink import inject

# Library libs
from fastybird_devices_module.repositories.channel import ChannelPropertiesRepository
from fastybird_devices_module.repositories.connector import (
    ConnectorPropertiesRepository,
)
from fastybird_devices_module.repositories.device import DevicePropertiesRepository
from fastybird_devices_module.state.property import (
    IChannelPropertyState,
    IConnectorPropertyState,
    IDevicePropertyState,
)


class IConnectorPropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for connector property

    @package        FastyBird:ConnectorsModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def get_by_id(self, property_id: uuid.UUID) -> Optional[IConnectorPropertyState]:
        """Find connector property state record by provided database identifier"""


class IDevicePropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for device property

    @package        FastyBird:DevicesModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def get_by_id(self, property_id: uuid.UUID) -> Optional[IDevicePropertyState]:
        """Find device property state record by provided database identifier"""


class IChannelPropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for channel property

    @package        FastyBird:DevicesModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def get_by_id(self, property_id: uuid.UUID) -> Optional[IChannelPropertyState]:
        """Find channel property state record by provided database identifier"""


@inject(
    bind={
        "repository": IConnectorPropertiesStatesRepository,
    }
)
class ConnectorPropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for connector property

    @package        FastyBird:ConnectorsModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __properties_repository: ConnectorPropertiesRepository
    __repository: Optional[IConnectorPropertiesStatesRepository]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        properties_repository: ConnectorPropertiesRepository,
        repository: Optional[IConnectorPropertiesStatesRepository] = None,
    ) -> None:
        self.__properties_repository = properties_repository
        self.__repository = repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[IConnectorPropertyState]:
        """Find connector property state record by provided database identifier"""
        if self.__repository is None:
            raise NotImplementedError("Connector properties states repository is not implemented")

        connector_property = self.__properties_repository.get_by_id(property_id=property_id)

        if connector_property is None:
            raise AttributeError("Connector property was not found in registry")

        return self.__repository.get_by_id(property_id=property_id)


@inject(
    bind={
        "repository": IDevicePropertiesStatesRepository,
    }
)
class DevicePropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for device property

    @package        FastyBird:DevicesModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __properties_repository: DevicePropertiesRepository
    __repository: Optional[IDevicePropertiesStatesRepository]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        properties_repository: DevicePropertiesRepository,
        repository: Optional[IDevicePropertiesStatesRepository] = None,
    ) -> None:
        self.__properties_repository = properties_repository
        self.__repository = repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[IDevicePropertyState]:
        """Find device property state record by provided database identifier"""
        if self.__repository is None:
            raise NotImplementedError("Device properties states repository is not implemented")

        device_property = self.__properties_repository.get_by_id(property_id=property_id)

        if device_property is None:
            raise AttributeError("Device property was not found in registry")

        if device_property.parent is not None:
            return self.__repository.get_by_id(property_id=device_property.parent.id)

        return self.__repository.get_by_id(property_id=property_id)


@inject(
    bind={
        "repository": IChannelPropertiesStatesRepository,
    }
)
class ChannelPropertiesStatesRepository(ABC):  # pylint: disable=too-few-public-methods
    """
    State repository for channel property

    @package        FastyBird:DevicesModule!
    @module         repositories/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __properties_repository: ChannelPropertiesRepository
    __repository: Optional[IChannelPropertiesStatesRepository]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        properties_repository: ChannelPropertiesRepository,
        repository: Optional[IChannelPropertiesStatesRepository] = None,
    ) -> None:
        self.__properties_repository = properties_repository
        self.__repository = repository

    # -----------------------------------------------------------------------------

    def get_by_id(self, property_id: uuid.UUID) -> Optional[IChannelPropertyState]:
        """Find channel property state record by provided database identifier"""
        if self.__repository is None:
            raise NotImplementedError("Channel properties states repository is not implemented")

        channel_property = self.__properties_repository.get_by_id(property_id=property_id)

        if channel_property is None:
            raise AttributeError("Channel property was not found in registry")

        if channel_property.parent is not None:
            return self.__repository.get_by_id(property_id=channel_property.parent.id)

        return self.__repository.get_by_id(property_id=property_id)
