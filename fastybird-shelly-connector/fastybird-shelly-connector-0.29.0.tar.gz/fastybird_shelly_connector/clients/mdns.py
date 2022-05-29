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
Shelly connector clients module mDNS client
"""

# Python base dependencies
import ipaddress
import logging
import re
import time
from typing import Optional, Union

# Library dependencies
from zeroconf import ServiceBrowser, Zeroconf

# Library libs
from fastybird_shelly_connector.clients.client import IClient
from fastybird_shelly_connector.consumers.consumer import Consumer
from fastybird_shelly_connector.consumers.entities import DeviceFoundEntity
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.registry.model import DevicesRegistry
from fastybird_shelly_connector.registry.records import (
    BlockRecord,
    DeviceRecord,
    SensorRecord,
)
from fastybird_shelly_connector.types import ClientType


class MdnsClient(IClient):  # pylint: disable=too-many-instance-attributes
    """
    mDNS client

    @package        FastyBird:ShellyConnector!
    @module         clients/mdns

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __consumer: Consumer

    __devices_registry: DevicesRegistry

    __logger: Union[Logger, logging.Logger]

    __common_zeroconf: Optional[Zeroconf]
    __zeroconf: Optional[Zeroconf]
    __browser_http: Optional[ServiceBrowser] = None  # pylint: disable=unused-private-member
    __browser_shelly: Optional[ServiceBrowser] = None  # pylint: disable=unused-private-member

    __MATCH_NAME = re.compile("(?P<devtype>shelly.+)-(?P<id>[0-9A-Fa-f]+)._(http|shelly)._tcp.local.")

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        consumer: Consumer,
        devices_registry: DevicesRegistry,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
        zeroconf: Optional[Zeroconf] = None,
    ) -> None:
        self.__consumer = consumer

        self.__devices_registry = devices_registry

        self.__common_zeroconf = zeroconf
        self.__zeroconf = None
        self.__browser_http = None  # pylint: disable=unused-private-member
        self.__browser_shelly = None  # pylint: disable=unused-private-member

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ClientType:
        """Client type"""
        return ClientType.MDNS

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start communication"""
        self.__zeroconf = zeroconf = self.__common_zeroconf or Zeroconf()
        self.__browser_http = ServiceBrowser(  # pylint: disable=unused-private-member
            zeroconf,
            "_http._tcp.local.",
            self,  # type: ignore[arg-type]
        )
        self.__browser_shelly = ServiceBrowser(  # pylint: disable=unused-private-member
            zeroconf,
            "_shelly._tcp.local.",
            self,  # type: ignore[arg-type]
        )

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop communication"""
        if self.__zeroconf:
            if not self.__common_zeroconf:
                try:
                    self.__zeroconf.close()

                except Exception:  # pylint: disable=broad-except
                    pass

            self.__zeroconf = None

        self.__browser_http = None  # pylint: disable=unused-private-member
        self.__browser_shelly = None  # pylint: disable=unused-private-member

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.__zeroconf is not None

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Send discover command"""

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process mDNS requests"""

    # -----------------------------------------------------------------------------

    def write_sensor(
        self,
        device_record: DeviceRecord,
        block_record: BlockRecord,
        sensor_record: SensorRecord,
        write_value: Union[str, int, float, bool, None],
    ) -> None:
        """Write value to device sensor"""

    # -----------------------------------------------------------------------------

    def remove_service(self, zeroconf: Zeroconf, service_type: str, service_name: str) -> None:
        """Remove mDns service from the collection"""

    # -----------------------------------------------------------------------------

    def add_service(self, zeroconf: Zeroconf, service_type: str, service_name: str) -> None:
        """Add mDns service in the collection"""
        test = self.__MATCH_NAME.fullmatch(service_name)

        if test:
            device_type = test.group("devtype")
            device_identifier = test.group("id")

            info = zeroconf.get_service_info(service_type, service_name)

            if info is not None:
                for address in info.addresses:
                    ip_address = str(ipaddress.IPv4Address(address))

                    self.__logger.debug(
                        "mDNS Type: %s, Id: %s, IP: %s",
                        device_type,
                        device_identifier,
                        ip_address,
                        extra={
                            "client": {
                                "type": ClientType.MDNS.value,
                            },
                            "device": {
                                "identifier": device_identifier,
                                "ip_address": ip_address,
                            },
                        },
                    )

                    device_record = self.__devices_registry.get_by_identifier(
                        device_identifier=device_identifier,
                    )

                    if device_record is not None:
                        self.__devices_registry.set_last_communication_timestamp(
                            device=device_record,
                            last_communication_timestamp=time.time(),
                        )

                    self.__consumer.append(
                        entity=DeviceFoundEntity(
                            device_identifier=device_identifier.lower(),
                            device_ip_address=ip_address,
                        ),
                    )

    # -----------------------------------------------------------------------------

    def update_service(self, zeroconf: Zeroconf, service_type: str, service_name: str) -> None:
        """Update mDns service in the collection"""
        self.add_service(zeroconf, service_type, service_name)
