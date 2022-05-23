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
import copy
import logging
from typing import Optional

from tikka.domains.entities.account import Account
from tikka.domains.entities.events import AccountEvent
from tikka.domains.events import EventDispatcher
from tikka.domains.wallets import Wallets
from tikka.interfaces.adapters.network.accounts import NetworkAccountsInterface
from tikka.interfaces.adapters.repository.accounts import AccountsRepositoryInterface
from tikka.interfaces.adapters.repository.file_wallets import (
    V1FileWalletsRepositoryInterface,
)


class Accounts:

    list: list = []

    """
    Account domain class
    """

    def __init__(
        self,
        repository: AccountsRepositoryInterface,
        network: NetworkAccountsInterface,
        wallets: Wallets,
        file_wallets_repository: V1FileWalletsRepositoryInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Accounts domain

        :param repository: AccountsRepositoryInterface instance
        :param network: NetworkAccountsInterface instance
        :param wallets: Wallets domain instance
        :param file_wallets_repository: FileWalletsRepository adapter instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.network = network
        self.wallets = wallets
        self.file_wallets_repository = file_wallets_repository
        self.event_dispatcher = event_dispatcher

        # init account list from database
        self.init_list()

    def init_list(self):
        """
        Init accounts from currency database connection

        :return:
        """
        # get accounts from database
        self.list = self.repository.list()

    def add(self, account: Account):
        """
        Add account

        :param account: Account instance
        :return:
        """
        # add account
        self.list.append(account)
        self.repository.add(account)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_ADD,
            copy.copy(account),
        )
        self.event_dispatcher.dispatch_event(event)

    def update(self, account: Account):
        """
        Update account

        :param account: Account instance
        :return:
        """
        self.repository.update(account)

    def get_by_index(self, index: int) -> Account:
        """
        Return account instance from index

        :param index: Index in account list
        :return:
        """
        return self.list[index]

    def get_by_address(self, address: str) -> Optional[Account]:
        """
        Return account instance from address

        :param address: Account address
        :return:
        """
        for account in self.list:
            if account.address == address:
                return account

        return None

    def delete(self, account: Account) -> None:
        """
        Delete account in list and repository

        :param account: Account instance to delete
        :return:
        """
        index = self.list.index(account)
        del self.list[index]
        self.repository.delete(account)
        self.wallets.delete(account.address)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_DELETE,
            copy.copy(account),
        )
        self.event_dispatcher.dispatch_event(event)

    def unlock(self, account: Account, wallet_password: str) -> bool:
        """
        Unlock account if password is OK

        :param account: Account instance
        :param wallet_password: Passphrase
        :return:
        """
        # get keypair from stored wallet
        try:
            keypair = self.wallets.get_keypair(account.address, wallet_password)
        except Exception as exception:
            logging.exception(exception)
            return False
        if keypair is None:
            return False

        # save keypair in account instance
        account.keypair = keypair

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_UPDATE,
            copy.copy(account),
        )
        self.event_dispatcher.dispatch_event(event)
        return True

    def lock(self, account: Account):
        """
        Lock account by removing keypair

        :param account: Account instance
        :return:
        """
        account.keypair = None

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_UPDATE,
            copy.copy(account),
        )
        self.event_dispatcher.dispatch_event(event)

    def fetch_balance_from_network(self, account: Account) -> None:
        """
        Fetch account balance from current EntryPoint connection

        :param account: Account instance
        :return:
        """
        balance = self.network.get_balance(account.address)
        if balance is not None:
            account.balance = balance
