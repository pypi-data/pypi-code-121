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

from dataclasses import dataclass
from typing import Optional, TypeVar

from substrateinterface import Keypair

AccountType = TypeVar("AccountType", bound="Account")


@dataclass
class Account:

    address: str
    uid: Optional[str] = None
    crypto_type: Optional[int] = None
    balance: Optional[int] = None
    _keypair: Optional[Keypair] = None
    _entropy: Optional[bytearray] = None

    @property
    def keypair(self) -> Optional[Keypair]:
        """
        Keypair instance getter

        :return:
        """
        return self._keypair

    @keypair.setter
    def keypair(self, keypair: Keypair):
        """
        Keypair instance setter

        :param keypair: Keypair instance
        :return:
        """
        self._keypair = keypair

    def __str__(self):
        """
        Return string representation

        :return:
        """
        if self.uid:
            return f"{self.address} - {self.uid}"
        return f"{self.address}"

    def __eq__(self, other):
        """
        Test equality on address

        :param other: Account instance
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return other.address == self.address

    def __hash__(self):
        return hash(self.address)
