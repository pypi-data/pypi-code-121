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
from pathlib import Path
from typing import Optional, Union

from duniterpy.key import SigningKey

from tikka.domains.entities.wallet import V1FileWallet
from tikka.interfaces.adapters.repository.file_wallets import (
    V1FileWalletsRepositoryInterface,
)


class V1FileWalletsRepository(V1FileWalletsRepositoryInterface):
    """
    V1FileWalletsRepository class
    """

    def load(
        self, path: Union[str, Path], password: Optional[str] = None
    ) -> V1FileWallet:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            V1FileWalletsRepositoryInterface.load.__doc__
        )
        if isinstance(path, str):
            path = Path(path)

        type_ = self.get_type(path)
        is_encrypted = type_ == "EWIF"
        signing_key: Optional[SigningKey] = None
        if not is_encrypted:
            if type_ == "WIF":
                signing_key = SigningKey.from_wif_file(str(path))
            elif type_ == "PUBSEC":
                signing_key = SigningKey.from_pubsec_file(str(path))
        elif password is not None:
            if type_ == "EWIF":
                signing_key = SigningKey.from_ewif_file(
                    str(path), password
                )  # type: ignore

        return V1FileWallet(path, type_, is_encrypted, signing_key)

    @staticmethod
    def get_type(path: Union[str, Path]) -> str:
        """
        Get format type of the V1 wallet file

        :param path: Path instance or string of the file
        :return:
        """
        if isinstance(path, str):
            path = Path(path)
        if path.suffix == ".dunikey":
            with path.open("r", encoding="utf-8") as file_handle:
                _type = file_handle.readline().strip()

                if "Type: EWIF" in _type:
                    type_ = "EWIF"
                elif "Type: WIF" in _type:
                    type_ = "WIF"
                elif "Type: PubSec" in _type:
                    type_ = "PUBSEC"

        return type_
