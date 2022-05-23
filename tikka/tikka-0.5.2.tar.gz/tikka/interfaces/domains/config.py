# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import abc
from typing import Any


class ConfigInterface(abc.ABC):
    """
    ConfigInterface class
    """

    CURRENCY_KEY = "currency"
    LANGUAGE_KEY = "language"
    ENTRY_POINTS_KEY = "entry_points"

    @abc.abstractmethod
    def set(self, name: str, value: Any) -> Any:
        """
        Set named parameter to value

        :param name: Name of parameter
        :param value: New value
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, name: str) -> Any:
        """
        Get value of named parameter

        :param name: Name of parameter
        :return:
        """
        raise NotImplementedError
