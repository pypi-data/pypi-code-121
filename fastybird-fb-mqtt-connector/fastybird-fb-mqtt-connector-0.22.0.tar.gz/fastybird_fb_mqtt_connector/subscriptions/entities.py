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
FastyBird MQTT connector subscriptions module entities
"""


class SubscriptionEntity:
    """
    Subscription entity

    @package        FastyBird:FbMqttConnector!
    @module         subscriptions/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __topic: str
    __qos: int
    __mid: int

    # -----------------------------------------------------------------------------

    def __init__(self, topic: str, qos: int, mid: int) -> None:
        self.__topic = topic
        self.__qos = qos
        self.__mid = mid

    # -----------------------------------------------------------------------------

    @property
    def topic(self) -> str:
        """Subscription topic string"""
        return self.__topic

    # -----------------------------------------------------------------------------

    @property
    def qos(self) -> int:
        """Subscription quality of service"""
        return self.__qos

    # -----------------------------------------------------------------------------

    @property
    def mid(self) -> int:
        """Subscription unique identifier"""
        return self.__mid
