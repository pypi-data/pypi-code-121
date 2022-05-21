from __future__ import annotations
import hashlib
import io
import re
from base64 import urlsafe_b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, IO, Union, Iterable, TypeVar, Callable, Mapping

from pkm.utils.io_streams import chunks
from pkm.utils.types import Hashable

_T = TypeVar("_T")
_K = TypeVar("_K")
_V = TypeVar("_V")
_H = TypeVar("_H", bound=Hashable)


class HashBuilder:
    def __init__(self):
        self._result = 7

    def regular(self, arg: _H) -> HashBuilder:
        """
        add the regular hash value of `arg` (computed by calling hash(arg))
        :param arg: the argument to add hash for
        :return: self for chaining
        """
        self._result = self._result * 31 + hash(arg)
        return self

    def regulars(self, *args: _H) -> HashBuilder:
        """
        add the regular hash value of each item in `args` (computed by calling hash(arg))
        :param args: the arguments to add hash for
        :return: self for chaining
        """
        return self.ordered_seq(args)

    def ordered_seq(self, seq: Iterable[_T], item_hash: Callable[[_T], int] = hash) -> HashBuilder:
        """
        adds an ordered sequence hash - computes a hash value for the given seq
        :param seq: the sequence to compute hash to
        :param item_hash: a function that can compute hash for the sequence items
        :return: self for chaining
        """
        result = self._result
        for item in seq:
            result = result * 31 + item_hash(item)
        self._result = result

        return self

    def unordered_seq(self, seq: Iterable[_T], item_hash: Callable[[_T], int] = hash) -> HashBuilder:
        """
        adds an unordered sequence hash - computes a hash value for the given seq
        :param seq: the sequence to compute hash to
        :param item_hash: a function that can compute hash for the sequence items
        :return: self for chaining
        """
        result = 7 * 31
        for item in seq:
            result ^= item_hash(item)

        self._result = self._result * 31 + result
        return self

    def unordered_mapping(
            self, m: Mapping[_K, _V], key_hash: Callable[[_K], int] = hash,
            value_hash: Callable[[_V], int] = hash) -> HashBuilder:
        """
        adds unordered maping hash - computes a hash value for the given dict, the hash will be the same for all dicts
        with the same elements without considering their insertion order
        :param m: the mapping to compute hash to
        :param key_hash: a function that can compute hash for the dict keys
        :param value_hash: a function that can compute hash for the dict values
        :return: self for chaining
        """
        result = 0
        for k, v in m.items():
            kvh = (7 * 31 + key_hash(k)) * 31 + value_hash(v)
            result ^= kvh

        self._result = self._result * 31 + result
        return self

    def build(self) -> int:
        """
        :return: the built hash
        """
        return self._result


_SIG_DELIM_RX = re.compile("\\s*=\\s*")


class HashDigester(Protocol):
    def digest(self) -> bytes:
        ...

    def hexdigest(self) -> str:
        ...

    def update(self, __data: Union[bytes, bytearray, memoryview]) -> None:
        ...


def stream(hd: HashDigester, file: Union[IO, Path], chunk_size: int = io.DEFAULT_BUFFER_SIZE):
    """
    streams a file into `hd` (via `hd.update(chunk)`) using chunks of the given `chunk_size`
    :param hd: the hash digester to stream into
    :param file: the file to stream
    :param chunk_size: the size of the chunk to use, defaults to `io.DEFAULT_BUFFER_SIZE`
    """
    if isinstance(file, Path):
        with file.open('rb') as source_fd:
            stream(hd, source_fd, chunk_size)
    else:
        for chunk in chunks(file, chunk_size):
            hd.update(chunk)


@dataclass
class HashSignature:
    hash_type: str
    hash_value: str

    def _encode_hash(self, hashd: HashDigester) -> str:
        return type(self).encode_hash(hashd)

    def validate_against(self, file: Path) -> bool:
        if not hasattr(hashlib, self.hash_type):
            raise KeyError(f"Cannot validate archive, Unsupported Hash {self.hash_type}")

        hash_computer = getattr(hashlib, self.hash_type)()
        stream(hash_computer, file)
        computed_hash = self._encode_hash(hash_computer)
        return computed_hash == self.hash_value

    def __str__(self):
        return f"{self.hash_type}={self.hash_value}"

    def __repr__(self):
        return f"HashSignature({self})"

    @classmethod
    def encode_hash(cls, hashd: HashDigester):
        return hashd.hexdigest()

    @classmethod
    def create_hex_encoded(cls, hash_type: str, hash_value: str):
        return HashSignature(hash_type, hash_value)

    @classmethod
    def compute_hex_encoded(cls, hash_function: str, file: Path) -> HashSignature:
        hashd = getattr(hashlib, hash_function)()
        stream(hashd, file)
        encoded = HashSignature.encode_hash(hashd)
        return HashSignature(hash_function, encoded)

    @classmethod
    def parse_hex_encoded(cls, signature: str) -> HashSignature:
        parts = _SIG_DELIM_RX.split(signature)
        if len(parts) != 2:
            raise ValueError('unsupported signature, expecting format <hash_type>=<hash_value>')

        return HashSignature(*parts)

    @classmethod
    def parse_urlsafe_base64_nopad_encoded(cls, signature: str) -> HashSignature:
        parts = _SIG_DELIM_RX.split(signature)
        if len(parts) != 2:
            raise ValueError(f'unsupported signature, expecting format <hash_type>=<hash_value>, got: {signature}')

        return _UrlsafeBase64NopadHashSignature(*parts)

    @classmethod
    def compute_urlsafe_base64_nopad_encoded(cls, hash_function: str, file: Path) -> HashSignature:
        hashd = getattr(hashlib, hash_function)()
        stream(hashd, file)
        encoded = _UrlsafeBase64NopadHashSignature.encode_hash(hashd)
        return _UrlsafeBase64NopadHashSignature(hash_function, encoded)

    @classmethod
    def create_urlsafe_base64_nopad_encoded(cls, hash_function: str, digest: HashDigester) -> HashSignature:
        return _UrlsafeBase64NopadHashSignature(hash_function, _UrlsafeBase64NopadHashSignature.encode_hash(digest))


class _UrlsafeBase64NopadHashSignature(HashSignature):

    @classmethod
    def encode_hash(cls, hashd: HashDigester):
        return urlsafe_b64encode(hashd.digest()).decode("latin1").rstrip("=")
