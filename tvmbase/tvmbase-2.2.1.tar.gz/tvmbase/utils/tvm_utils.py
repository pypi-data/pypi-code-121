import re

from tvmbase.constants import ADDRESS_REGEX


def is_address(string: str) -> bool:
    return bool(re.fullmatch(ADDRESS_REGEX, string))


def decode_bytes(value: str) -> str:
    return bytes.fromhex(value).decode()
