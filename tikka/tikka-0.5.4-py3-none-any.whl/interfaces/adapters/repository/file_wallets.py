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
from pathlib import Path
from typing import Optional, Union

from tikka.domains.entities.wallet import V1FileWallet


class V1FileWalletsRepositoryInterface(abc.ABC):
    """
    V1FileWalletsRepositoryInterface class
    """

    @abc.abstractmethod
    def load(
        self, path: Union[str, Path], password: Optional[str] = None
    ) -> V1FileWallet:
        """
        Return data Wallet instance

        :param path: Path instance or string of the file
        :param password: Password for encrypted file
        :return:
        """
        raise NotImplementedError
