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
Tuya connector consumers module consumers proxy
"""

# Python base dependencies
import logging
from abc import ABC, abstractmethod
from queue import Full as QueueFull
from queue import Queue
from typing import List, Set, Union

# Library libs
from fastybird_tuya_connector.consumers.entities import BaseEntity
from fastybird_tuya_connector.exceptions import InvalidStateException
from fastybird_tuya_connector.logger import Logger


class IConsumer(ABC):  # pylint: disable=too-few-public-methods
    """
    Messages consumer interface

    @package        FastyBird:TuyaConnector!
    @module         consumers/consumer

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def consume(self, entity: BaseEntity) -> None:
        """Handle received entity"""


class Consumer:
    """
    Messages consumers proxy

    @package        FastyBird:TuyaConnector!
    @module         consumers/consumer

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __consumers: Set[IConsumer]

    __queue: Queue

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        consumers: List[IConsumer],
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__consumers = set(consumers)

        self.__logger = logger

        self.__queue = Queue(maxsize=1000)

    # -----------------------------------------------------------------------------

    def append(self, entity: BaseEntity) -> None:
        """Append new entity for handle"""
        try:
            self.__queue.put(item=entity)

        except QueueFull:
            self.__logger.error("Connector consumer processing queue is full. New messages could not be added")

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle received message"""
        try:
            if not self.__queue.empty():
                entity = self.__queue.get()

                if isinstance(entity, BaseEntity):
                    for consumer in self.__consumers:
                        consumer.consume(entity=entity)

        except InvalidStateException as ex:
            self.__logger.error(
                "Received message could not be consumed",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Check if all messages were handled"""
        return self.__queue.empty()
