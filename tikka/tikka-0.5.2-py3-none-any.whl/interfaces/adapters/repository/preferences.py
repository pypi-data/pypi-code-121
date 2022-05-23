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
from typing import Optional

SELECTED_TAB_PAGE_KEY = "selected_tab_page"
WALLET_LOAD_DEFAULT_DIRECTORY = "wallet_load_default_directory"
WALLET_SAVE_DEFAULT_DIRECTORY = "wallet_save_default_directory"
CURRENT_ENTRY_POINT_URL = "current_entry_point_url"
SELECTED_UNIT = "selected_unit"


class PreferencesRepositoryInterface(abc.ABC):
    """
    PreferencesRepositoryInterface class
    """

    @abc.abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        Return the key value

        :param key: Key name
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, value: str) -> None:
        """
        Set the key value

        :param key: Key name
        :param value: Value to store
        :return:
        """
        raise NotImplementedError
