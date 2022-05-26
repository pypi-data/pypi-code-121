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

"""
Dewif lib module
"""
import base64
import hashlib
import random
import struct
from dataclasses import dataclass

from duniterpy.key.scrypt_params import ScryptParams
from mnemonic import Mnemonic

DEWIF_CURRENCY_CODE_NONE = 0x00000000
DEWIF_CURRENCY_CODE_G1 = 0x00000001
DEWIF_CURRENCY_CODE_G1_TEST = 0x10000001
DEWIF_ALGORITHM_CODE_ED25519 = 0x00
DEWIF_ALGORITHM_CODE_BIP32_ED25519 = 0x01
DEWIF_MNEMONIC_LANGUAGES = {
    0: "english",
    1: "chinese_simplified",
    2: "chinese_traditional",
    3: "french",
    4: "italian",
    5: "japanese",
    6: "korean",
    7: "spanish",
}


def random_bytes(size: int) -> bytes:
    """
    Return random bytes of given length

    :param size: Size of nonce in bytes
    :return:
    """
    return bytearray(random.getrandbits(8) for _ in range(size))


def byte_xor(bytes1, bytes2):
    """
    XOR two byte strings

    :param bytes1: First string
    :param bytes2: Second string
    :return:
    """
    return bytes([_a ^ _b for _a, _b in zip(bytes1, bytes2)])


def scrypt_maxmem(n_value, r_value, p_value):
    """
    Get sufficient maxmem scrypt parameter

    :param n_value: N value
    :param r_value: r value
    :param p_value: p value
    :return:
    """
    return 128 * r_value * (n_value + p_value + 2)


@dataclass
class DewifV1:
    """
    Dewif master class
    """

    password: str
    currency: int
    log_n: int

    version = 1

    def __bytes__(self) -> bytes:
        raise NotImplementedError

    def __str__(self) -> str:
        return base64.b64encode(bytes(self)).decode("utf-8")

    def __repr__(self):
        return f"class Ed25519 ({self.__str__()})"


@dataclass
class Ed25519V1(DewifV1):
    """
    Ed25519 algorithm class
    """

    seed: bytes
    pubkey: bytes

    algorithm = DEWIF_ALGORITHM_CODE_ED25519

    def __bytes__(self):
        nonce = random_bytes(12)

        # # test RFC
        # nonce = 0x013194f1286512cf094295cb.to_bytes(12, "big")

        header = struct.pack(">ii", self.version, self.currency)
        data = (
            header
            + self.log_n.to_bytes(1, "big")
            + self.algorithm.to_bytes(1, "big")
            + nonce
        )

        scrypt_params = ScryptParams()
        n_param = pow(2, self.log_n)
        salt = b"dewif" + nonce + self.password.encode("utf-8")
        xor_key = hashlib.scrypt(
            password=self.password.encode("utf-8"),
            salt=hashlib.sha256(salt).digest(),
            n=n_param,
            r=scrypt_params.r,  # 16
            p=scrypt_params.p,  # 1
            dklen=64,
            maxmem=scrypt_maxmem(n_param, scrypt_params.r, scrypt_params.p),
        )
        data_to_encrypt = self.seed + self.pubkey
        encrypted_data = byte_xor(data_to_encrypt, xor_key)
        data += encrypted_data

        # test RFC
        # assert base64.b64encode(data).decode("utf-8") == \
        # "AAAAARAAAAEMAAExlPEoZRLPCUKVy0iKnn1HUSFcmhwJPQETAghFDvH8ZmX59IuvR9hYV1gnVjCpU+TGOdUzyQmj3+auw3vUpFQYBiRlh67/I1xAhZM="

        return data


@dataclass
class Bip32Ed25519V1(DewifV1):
    """
    BIP32-Ed25519 algorithm class
    """

    mnemonic: str
    language: str

    algorithm = DEWIF_ALGORITHM_CODE_BIP32_ED25519

    def __bytes__(self):
        nonce = random_bytes(12)

        # test RFC
        # nonce = 0xc54299ae71fe2a4ecdc7d58a.to_bytes(12, "big")

        header = struct.pack(">ii", self.version, self.currency)
        data = (
            header
            + self.log_n.to_bytes(1, "big")
            + self.algorithm.to_bytes(1, "big")
            + nonce
        )

        scrypt_params = ScryptParams()
        n_param = pow(2, self.log_n)
        salt = b"dewif" + nonce + self.password.encode("utf-8")
        xor_key = hashlib.scrypt(
            password=self.password.encode("utf-8"),
            salt=hashlib.sha256(salt).digest(),
            n=pow(2, self.log_n),
            r=scrypt_params.r,  # 16
            p=scrypt_params.p,  # 1
            dklen=42,
            maxmem=scrypt_maxmem(n_param, scrypt_params.r, scrypt_params.p),
        )

        entropy = Mnemonic(self.language).to_entropy(self.mnemonic)
        entropy_length = len(entropy)
        entropy_padding = random_bytes(32 - entropy_length)

        # test RFC
        # entropy_padding = 0xaa083bd16c8317121d34b5aed1c1420a.to_bytes(16, "big")

        language_code = list(DEWIF_MNEMONIC_LANGUAGES.keys())[
            list(DEWIF_MNEMONIC_LANGUAGES.values()).index(self.language)
        ]
        checksum = hashlib.sha256(
            nonce
            + language_code.to_bytes(1, "big")
            + entropy_length.to_bytes(1, "big")
            + entropy
        ).digest()[:8]

        data_to_encrypt = (
            language_code.to_bytes(1, "big")
            + entropy_length.to_bytes(1, "big")
            + entropy
            + entropy_padding
            + checksum
        )
        encrypted_data = byte_xor(data_to_encrypt, xor_key)
        data += encrypted_data

        # test RFC
        # assert base64.b64encode(data).decode("utf-8") == \
        # "AAAAARAAAAEOAcVCma5x/ipOzcfViufNdfj5k4Sl5zdrHLf9PPGDkH1Pz3y8tFrx/jZZcJd92LIk+EWIrjxiSw=="

        return data
