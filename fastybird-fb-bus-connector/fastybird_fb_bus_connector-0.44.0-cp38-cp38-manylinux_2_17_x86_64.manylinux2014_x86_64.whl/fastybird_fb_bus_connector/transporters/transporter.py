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
FastyBird BUS connector transporters module proxy
"""

# Python base dependencies
from abc import ABC, abstractmethod
from typing import List


class ITransporter(ABC):
    """
    Transporter interface

    @package        FastyBird:FbBusConnector!
    @module         transporters/transporter

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @property
    @abstractmethod
    def packet_to_be_sent(self) -> int:
        """Number of packets waiting in queue"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def broadcast_packet(self, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Broadcast packet to all devices"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def send_packet(self, address: int, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Send packet to specific device address"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Process transporter requests"""
