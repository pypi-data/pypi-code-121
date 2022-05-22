import re

ADDRESS_REGEX = re.compile(r'(0|-1):[0-9a-f]{64}')


def is_address(string: str) -> bool:
    return bool(re.fullmatch(ADDRESS_REGEX, string))


def decode_bytes(value: str) -> str:
    return bytes.fromhex(value).decode()
