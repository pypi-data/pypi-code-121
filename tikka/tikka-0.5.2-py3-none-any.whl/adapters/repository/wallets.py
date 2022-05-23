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

from typing import List, Optional

from tikka.adapters.repository.sqlite3 import Sqlite3RepositoryInterface
from tikka.domains.entities.wallet import Wallet
from tikka.interfaces.adapters.repository.wallets import WalletsRepositoryInterface

TABLE_NAME = "wallets"


class Sqlite3WalletsRepository(WalletsRepositoryInterface, Sqlite3RepositoryInterface):
    """
    Sqlite3WalletsRepository class
    """

    def list(self) -> List[Wallet]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.list.__doc__
        )

        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME}")

        list_ = []
        for row in result_set:
            list_.append(Wallet(*row))

        return list_

    def add(self, wallet: Wallet) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **{
                key: value
                for (key, value) in wallet.__dict__.items()
                if not key.startswith("_")
            },
        )

    def get(self, address: str) -> Optional[Wallet]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE address=?", (address,)
        )
        if row is None:
            return None

        return Wallet(*row)

    def update(self, wallet: Wallet) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"address='{wallet.address}'",
            **{
                key: value
                for (key, value) in wallet.__dict__.items()
                if not key.startswith("_")
            },
        )

    def delete(self, address: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, address=address)

    def exists(self, address: str) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WalletsRepositoryInterface.exists.__doc__
        )

        row = self.client.select_one(
            f"SELECT count(address) FROM {TABLE_NAME} WHERE address=?", (address,)
        )
        if row is None:
            return False

        return row[0] == 1
