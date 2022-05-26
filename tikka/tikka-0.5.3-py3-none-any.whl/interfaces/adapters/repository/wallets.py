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
from typing import List, Optional

from tikka.domains.entities.wallet import Wallet


class WalletsRepositoryInterface(abc.ABC):
    """
    AccountRepositoryInterface class
    """

    @abc.abstractmethod
    def list(self) -> List[Wallet]:
        """
        List wallets from repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, wallet: Wallet) -> None:
        """
        Add a new wallet in repository

        :param wallet: Wallet instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, address: str) -> Optional[Wallet]:
        """
        Return Wallet instance from repository

        :param address: Wallet address
        :return:
        """
        raise NotImplementedError

    def update(self, wallet: Wallet) -> None:
        """
        Update wallet in repository

        :param wallet: Wallet instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, address: str) -> None:
        """
        Delete wallet in repository

        :param address: Wallet address to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, address: str) -> bool:
        """
        Return True if wallet with address is in repository, else False

        :param address: Wallet address to check
        :return:
        """
        raise NotImplementedError
