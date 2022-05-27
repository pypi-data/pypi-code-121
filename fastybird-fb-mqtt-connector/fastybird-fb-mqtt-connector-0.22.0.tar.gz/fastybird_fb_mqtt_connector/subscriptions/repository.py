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
FastyBird MQTT connector subscriptions module repositories
"""

# Python base dependencies
from typing import Dict, List, Optional

# Library libs
from fastybird_fb_mqtt_connector.subscriptions.entities import SubscriptionEntity


class SubscriptionsRepository:
    """
    Subscriptions repository

    @package        FastyBird:FbMqttConnector!
    @module         subscriptions/repository

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[int, SubscriptionEntity] = {}

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def get_by_id(self, mid: int) -> Optional[SubscriptionEntity]:
        """Get topic subscription by message identifier"""
        if mid in self.__items:
            return self.__items[mid]

        return None

    # -----------------------------------------------------------------------------

    def create(self, topic: str, qos: int, mid: int) -> SubscriptionEntity:
        """Create new topic subscription"""
        subscription = SubscriptionEntity(topic=topic, qos=qos, mid=mid)

        self.__items[mid] = subscription

        return subscription

    # -----------------------------------------------------------------------------

    def delete(self, subscription: SubscriptionEntity) -> None:
        """Delete topic subscription"""
        del self.__items[subscription.mid]

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "SubscriptionsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> SubscriptionEntity:
        if self.__iterator_index < len(self.__items.values()):
            items: List[SubscriptionEntity] = list(self.__items.values())

            result = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration
