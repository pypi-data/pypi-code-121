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
from typing import Optional

from tikka.adapters.repository.sqlite3 import Sqlite3RepositoryInterface
from tikka.interfaces.adapters.repository.preferences import (
    PreferencesRepositoryInterface,
)

TABLE_NAME = "preferences"


class Sqlite3PreferencesRepository(
    PreferencesRepositoryInterface, Sqlite3RepositoryInterface
):
    """
    Sqlite3PreferencesRepository class
    """

    def get(self, key: str) -> Optional[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.get.__doc__
        )

        result = self.client.select_one(
            f"SELECT value_ FROM {TABLE_NAME} WHERE key_=?", (key,)
        )
        if result is None:
            return None

        return result[0]

    def set(self, key: str, value: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.get.__doc__
        )

        self.client.update(TABLE_NAME, f"key_='{key}'", value_=value)
