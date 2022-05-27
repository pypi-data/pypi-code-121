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
Devices module DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from asyncio import AbstractEventLoop

from fastybird_exchange.consumer import Consumer
from kink import di
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.connectors.connector import Connector
from fastybird_devices_module.connectors.consumer import ConnectorConsumer
from fastybird_devices_module.connectors.queue import ConnectorQueue
from fastybird_devices_module.logger import Logger
from fastybird_devices_module.managers.channel import (
    ChannelControlsManager,
    ChannelPropertiesManager,
    ChannelsManager,
)
from fastybird_devices_module.managers.connector import (
    ConnectorControlsManager,
    ConnectorPropertiesManager,
    ConnectorsManager,
)
from fastybird_devices_module.managers.device import (
    DeviceAttributesManager,
    DeviceControlsManager,
    DevicePropertiesManager,
    DevicesManager,
)
from fastybird_devices_module.managers.state import (
    ChannelPropertiesStatesManager,
    ConnectorPropertiesStatesManager,
    DevicePropertiesStatesManager,
)
from fastybird_devices_module.repositories.channel import (
    ChannelControlsRepository,
    ChannelPropertiesRepository,
    ChannelsRepository,
)
from fastybird_devices_module.repositories.connector import (
    ConnectorControlsRepository,
    ConnectorPropertiesRepository,
    ConnectorsRepository,
)
from fastybird_devices_module.repositories.device import (
    DeviceAttributesRepository,
    DeviceControlsRepository,
    DevicePropertiesRepository,
    DevicesRepository,
)
from fastybird_devices_module.repositories.state import (
    ChannelPropertiesStatesRepository,
    ConnectorPropertiesStatesRepository,
    DevicePropertiesStatesRepository,
)
from fastybird_devices_module.subscriber import (
    EntitiesSubscriber,
    EntityCreatedSubscriber,
)


def register_services(  # pylint: disable=too-many-statements
    loop: AbstractEventLoop,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> None:
    """Register devices module services"""
    if OrmSession not in di:
        logger.error("SQLAlchemy database session is not registered in container!")

        return

    di[Logger] = Logger(logger=logger)
    di["fb-devices-module_logger"] = di[Logger]

    # Entities repositories

    di[ConnectorsRepository] = ConnectorsRepository(session=di[OrmSession])
    di["fb-devices-module_connectors-repository"] = di[ConnectorsRepository]
    di[ConnectorPropertiesRepository] = ConnectorPropertiesRepository(session=di[OrmSession])
    di["fb-devices-module_connector-properties-repository"] = di[ConnectorPropertiesRepository]
    di[ConnectorControlsRepository] = ConnectorControlsRepository(session=di[OrmSession])
    di["fb-devices-module_connector-controls-repository"] = di[ConnectorControlsRepository]
    di[DevicesRepository] = DevicesRepository(session=di[OrmSession])
    di["fb-devices-module_devices-repository"] = di[DevicesRepository]
    di[DevicePropertiesRepository] = DevicePropertiesRepository(session=di[OrmSession])
    di["fb-devices-module_device-properties-repository"] = di[DevicePropertiesRepository]
    di[DeviceControlsRepository] = DeviceControlsRepository(session=di[OrmSession])
    di["fb-devices-module_device-controls-repository"] = di[DeviceControlsRepository]
    di[DeviceAttributesRepository] = DeviceAttributesRepository(session=di[OrmSession])
    di["fb-devices-module_device-attributes-repository"] = di[DeviceAttributesRepository]
    di[ChannelsRepository] = ChannelsRepository(session=di[OrmSession])
    di["fb-devices-module_channels-repository"] = di[ChannelsRepository]
    di[ChannelPropertiesRepository] = ChannelPropertiesRepository(session=di[OrmSession])
    di["fb-devices-module_channel-properties-repository"] = di[ChannelPropertiesRepository]
    di[ChannelControlsRepository] = ChannelControlsRepository(session=di[OrmSession])
    di["fb-devices-module_channel-controls-repository"] = di[ChannelControlsRepository]

    # States repositories

    di[ConnectorPropertiesStatesRepository] = ConnectorPropertiesStatesRepository(
        properties_repository=di[ConnectorPropertiesRepository],
    )
    di["fb-devices-module_connector-properties-states-repository"] = di[ConnectorPropertiesStatesRepository]
    di[DevicePropertiesStatesRepository] = DevicePropertiesStatesRepository(
        properties_repository=di[DevicePropertiesRepository],
    )
    di["fb-devices-module_device-properties-states-repository"] = di[DevicePropertiesStatesRepository]
    di[ChannelPropertiesStatesRepository] = ChannelPropertiesStatesRepository(
        properties_repository=di[ChannelPropertiesRepository],
    )
    di["fb-devices-module_channel-properties-states-repository"] = di[ChannelPropertiesStatesRepository]

    # Entities managers

    di[ConnectorsManager] = ConnectorsManager(session=di[OrmSession])
    di["fb-devices-module_connectors-manager"] = di[ConnectorsManager]
    di[ConnectorPropertiesManager] = ConnectorPropertiesManager(session=di[OrmSession])
    di["fb-devices-module_connector-properties-manager"] = di[ConnectorPropertiesManager]
    di[ConnectorControlsManager] = ConnectorControlsManager(session=di[OrmSession])
    di["fb-devices-module_connector-controls-manager"] = di[ConnectorControlsManager]
    di[DevicesManager] = DevicesManager(session=di[OrmSession])
    di["fb-devices-module_devices-manager"] = di[DevicesManager]
    di[DevicePropertiesManager] = DevicePropertiesManager(session=di[OrmSession])
    di["fb-devices-module_device-properties-manager"] = di[DevicePropertiesManager]
    di[DeviceControlsManager] = DeviceControlsManager(session=di[OrmSession])
    di["fb-devices-module_device-controls-manager"] = di[DeviceControlsManager]
    di[DeviceAttributesManager] = DeviceAttributesManager(session=di[OrmSession])
    di["fb-devices-module_device-attributes-manager"] = di[DeviceAttributesManager]
    di[ChannelsManager] = ChannelsManager(session=di[OrmSession])
    di["fb-devices-module_channels-manager"] = di[ChannelsManager]
    di[ChannelPropertiesManager] = ChannelPropertiesManager(session=di[OrmSession])
    di["fb-devices-module_channel-properties-manager"] = di[ChannelPropertiesManager]
    di[ChannelControlsManager] = ChannelControlsManager(session=di[OrmSession])
    di["fb-devices-module_channel-controls-manager"] = di[ChannelControlsManager]

    # States managers

    di[ConnectorPropertiesStatesManager] = ConnectorPropertiesStatesManager()
    di["fb-devices-module_connector-properties-states-manager"] = di[ConnectorPropertiesStatesManager]
    di[DevicePropertiesStatesManager] = DevicePropertiesStatesManager()
    di["fb-devices-module_device-properties-states-manager"] = di[DevicePropertiesStatesManager]
    di[ChannelPropertiesStatesManager] = ChannelPropertiesStatesManager(
        repository=di[ChannelPropertiesRepository],
    )
    di["fb-devices-module_channel-properties-states-manager"] = di[ChannelPropertiesStatesManager]

    # Entities subscribers

    di[EntitiesSubscriber] = EntitiesSubscriber(
        connector_properties_states_repository=di[ConnectorPropertiesStatesRepository],
        connector_properties_states_manager=di[ConnectorPropertiesStatesManager],
        device_properties_states_repository=di[DevicePropertiesStatesRepository],
        device_properties_states_manager=di[DevicePropertiesStatesManager],
        channel_properties_states_repository=di[ChannelPropertiesStatesRepository],
        channel_properties_states_manager=di[ChannelPropertiesStatesManager],
        session=di[OrmSession],
    )
    di["fb-devices-module_entities-subscriber"] = di[EntitiesSubscriber]
    di[EntityCreatedSubscriber] = EntityCreatedSubscriber()
    di["fb-devices-module_entity-created-subscriber"] = di[EntityCreatedSubscriber]

    # Module connector

    di[ConnectorQueue] = ConnectorQueue(logger=di[Logger])
    di["fb-devices-module_connector-queue"] = di[ConnectorQueue]
    di[ConnectorConsumer] = ConnectorConsumer(queue=di[ConnectorQueue], logger=di[Logger])
    di["fb-devices-module_connector-consumer"] = di[ConnectorConsumer]

    di[Connector] = Connector(
        queue=di[ConnectorQueue],
        devices_repository=di[DevicesRepository],
        devices_properties_repository=di[DevicePropertiesRepository],
        devices_control_repository=di[DeviceControlsRepository],
        devices_attributes_repository=di[DeviceAttributesRepository],
        channels_repository=di[ChannelsRepository],
        channels_properties_repository=di[ChannelPropertiesRepository],
        channels_control_repository=di[ChannelControlsRepository],
        connectors_repository=di[ConnectorsRepository],
        connectors_properties_repository=di[ConnectorPropertiesRepository],
        connectors_properties_manager=di[ConnectorPropertiesManager],
        connectors_control_repository=di[ConnectorControlsRepository],
        connectors_properties_states_repository=di[ConnectorPropertiesStatesRepository],
        connectors_properties_states_manager=di[ConnectorPropertiesStatesManager],
        logger=di[Logger],
        loop=loop,
    )
    di["fb-devices-module_connector-handler"] = di[Connector]

    # Check for presence of exchange consumer proxy
    if Consumer in di:
        # Register connector exchange consumer into consumer proxy
        di[Consumer].register_consumer(di[ConnectorConsumer])
