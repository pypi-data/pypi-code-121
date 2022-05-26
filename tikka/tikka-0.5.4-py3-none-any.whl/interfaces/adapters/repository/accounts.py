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
from typing import List

from tikka.domains.entities.account import Account


class AccountsRepositoryInterface(abc.ABC):
    """
    AccountRepositoryInterface class
    """

    @abc.abstractmethod
    def add(self, account: Account) -> None:
        """
        Add a new account in repository

        :param account: Account instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Account]:
        """
        List accounts from repository

        :return:
        """
        raise NotImplementedError

    def update(self, account: Account) -> None:
        """
        Update account in repository

        :param account: Account instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, account: Account) -> None:
        """
        Delete account in repository

        :param account: Account instance to delete
        :return:
        """
        raise NotImplementedError
