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
import hashlib
import random
import string

from mnemonic import Mnemonic

from tikka.domains.entities.constants import MNEMONIC_LANGUAGES


def generate_alphabetic(size: int = 5) -> str:
    """
    Generate alphabetic secret of size

    :param size: Size of secret (default=5)
    :return:
    """
    return "".join(random.choice(string.ascii_letters).upper() for _ in range(size))


def generate_mnemonic(language: str) -> str:
    """
    Generate 128 bits BIP39 Mnemonic passphrase using language words

    see https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
    and https://github.com/trezor/python-mnemonic/tree/master/mnemonic/wordlist

    :param language: Language name use in the official Python implementation
    :return:
    """
    mnemonic_language = MNEMONIC_LANGUAGES[language]
    mnemonic = Mnemonic(mnemonic_language)
    return mnemonic.generate(strength=128)


def generate_dubp_scrypt_salt(mnemonic: str):
    """
    Return the DUBP salt from mnemonic secret
    see RFC 0014 https://git.duniter.org/documents/rfcs/blob/dubp-mnemonic/rfc/0014_Dubp_Mnemonic.md

    :param mnemonic: DUBP mnemonic secret
    :return:
    """
    return hashlib.sha256(b"dubp" + mnemonic.encode("utf-8")).digest()
