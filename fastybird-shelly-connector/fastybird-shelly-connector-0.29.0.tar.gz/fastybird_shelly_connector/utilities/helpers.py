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
Shelly connector helpers module
"""

# Python base dependencies
from datetime import datetime, timedelta
from typing import Optional


class Timer:
    """
    Loop timer

    @package        FastyBird:ShellyConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __last_time: Optional[datetime] = None
    __interval: Optional[timedelta] = None

    # -----------------------------------------------------------------------------

    def __init__(self, interval: int) -> None:
        self.set_interval(interval)

        self.__last_time = None

    # -----------------------------------------------------------------------------

    def set_interval(self, interval: int) -> None:
        """Set timer interval in seconds"""
        self.__interval = timedelta(seconds=interval)

    # -----------------------------------------------------------------------------

    def check(self) -> bool:
        """Check if interval is reached"""
        if self.__interval is not None:
            now = datetime.now()

            if self.__last_time is None or now - self.__last_time > self.__interval:
                self.__last_time = now

                return True

        return False
