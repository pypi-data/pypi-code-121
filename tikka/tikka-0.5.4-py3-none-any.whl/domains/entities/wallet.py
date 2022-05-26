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
from pathlib import Path
from typing import Optional

from duniterpy.key import SigningKey

WALLET_TYPES = {
    "PUBSEC": "PubSec: a file with your secret and public key",
    "WIF": "WIF: a file with your seed",
    "EWIF": "EWIF: an encrypted file with your seed, need a password",
    "DEWIF": "DEWIF: an encrypted file with your seed, need a password",
}


@dataclass
class V1FileWallet:
    path: Path
    type: str
    is_encrypted: bool = False
    signing_key: Optional[SigningKey] = None


@dataclass
class Wallet:
    address: str
    crypto_type: int
    encrypted_private_key: str
    encryption_nonce: str
    encryption_mac_tag: str
