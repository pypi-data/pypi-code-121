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
FastyBird BUS connector receivers module proxy
"""

# Python base dependencies
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Set, Union

# Library libs
from fastybird_fb_bus_connector.consumers.consumer import Consumer
from fastybird_fb_bus_connector.consumers.entities import BaseEntity
from fastybird_fb_bus_connector.exceptions import ParsePayloadException
from fastybird_fb_bus_connector.logger import Logger


class IReceiver(ABC):  # pylint: disable=too-few-public-methods
    """
    Data receiver interface

    @package        FastyBird:FbBusConnector!
    @module         receivers/receiver

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @abstractmethod
    def receive(self, payload: bytearray, length: int, address: Optional[int]) -> Optional[BaseEntity]:
        """Handle received entity"""


class Receiver:  # pylint: disable=too-few-public-methods
    """
    BUS messages receivers proxy

    @package        FastyBird:FbBusConnector!
    @module         receivers/receiver

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __receivers: Set[IReceiver]
    __consumer: Consumer

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        receivers: List[IReceiver],
        consumer: Consumer,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__receivers = set(receivers)
        self.__consumer = consumer

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def on_message(
        self,
        payload: bytearray,
        length: int,
        address: Optional[int],
    ) -> None:
        """Handle received message"""
        for receiver in self.__receivers:
            try:
                result = receiver.receive(payload=payload, length=length, address=address)

                if result is not None:
                    self.__consumer.append(entity=result)

                    return

            except ValueError as ex:
                self.__logger.error(
                    "Value error occurred during message parsing",
                    extra={
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    },
                )
                self.__logger.exception(ex)

            except ParsePayloadException as ex:
                self.__logger.error(
                    "Received message could not be successfully parsed to entity",
                    extra={
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    },
                )
                self.__logger.exception(ex)
