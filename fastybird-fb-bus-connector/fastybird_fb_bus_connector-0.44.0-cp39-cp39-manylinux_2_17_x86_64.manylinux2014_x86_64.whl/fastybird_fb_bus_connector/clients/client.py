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
FastyBird BUS connector clients module proxy
"""

# Python base dependencies
from abc import ABC, abstractmethod
from typing import List, Set


class IClient(ABC):  # pylint: disable=too-few-public-methods
    """
    Communication client interface

    @package        FastyBird:FbBusConnector!
    @module         clients/client

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def enable_discovery(self) -> None:
        """Enable client devices discovery"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def disable_discovery(self) -> None:
        """Disable client devices discovery"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Handle client communication"""


class Client:  # pylint: disable=too-few-public-methods
    """
    Client proxy

    @package        FastyBird:FbBusConnector!
    @module         clients/client

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __clients: Set[IClient]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        clients: List[IClient],
    ) -> None:
        self.__clients = set(clients)

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Discover new devices"""
        for client in self.__clients:
            client.enable_discovery()

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle clients communication"""
        # Check for processing queue
        for client in self.__clients:
            client.handle()
