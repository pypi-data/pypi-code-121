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
from typing import List

from tikka.adapters.repository.sqlite3 import Sqlite3RepositoryInterface
from tikka.domains.entities.tab import Tab
from tikka.interfaces.adapters.repository.tabs import TabRepositoryInterface

TABLE_NAME = "tabs"


class Sqlite3TabRepository(TabRepositoryInterface, Sqlite3RepositoryInterface):
    """
    Sqlite3TabRepository class
    """

    def add(self, tab: Tab) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TabRepositoryInterface.add.__doc__
        )

        self.client.insert(
            TABLE_NAME,
            **{
                key: value
                for (key, value) in tab.__dict__.items()
                if not key.startswith("_")
            },
        )

    def delete(self, id: str) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TabRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, id=id)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TabRepositoryInterface.delete_all.__doc__
        )
        # remove all entries
        self.client.clear(TABLE_NAME)

    def list(self) -> List[Tab]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TabRepositoryInterface.list.__doc__
        )

        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME}")

        list_: List[Tab] = []
        for row in result_set:
            list_.append(Tab(*row))

        return list_
