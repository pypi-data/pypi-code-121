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
FastyBird BUS connector receivers module receiver for API v1
"""

# Python base dependencies
from typing import Optional

# Library libs
from fastybird_fb_bus_connector.api.v1parser import V1Parser
from fastybird_fb_bus_connector.api.v1validator import V1Validator
from fastybird_fb_bus_connector.consumers.entities import BaseEntity
from fastybird_fb_bus_connector.receivers.receiver import IReceiver


class ApiV1Receiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    BUS receiver for API v1

    @package        FastyBird:FbBusConnector!
    @module         receivers/apiv1

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __parser: V1Parser

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        parser: V1Parser,
    ) -> None:
        self.__parser = parser

    # -----------------------------------------------------------------------------

    def receive(self, payload: bytearray, length: int, address: Optional[int]) -> Optional[BaseEntity]:
        if V1Validator.validate_version(payload=payload) is False:
            return None

        if V1Validator.validate(payload=payload) is False:
            return None

        return self.__parser.parse_message(
            payload=payload,
            length=length,
            address=address,
        )
