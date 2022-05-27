from secrets import token_bytes
from coincurve import PublicKey
from sha3 import keccak_256
import random
import string
from typing import Union, Any


def address_pk() -> Any:
    """
    Generate new private key and public address for ethereum network
    :return: private key, public address
    """
    private_key = keccak_256(token_bytes(32)).digest()
    public_key = PublicKey.from_valid_secret(private_key).format(compressed=False)[1:]
    addr = keccak_256(public_key).digest()[-20:]
    return private_key.hex(), addr.hex()


def address() -> Any:
    """
    Generate new public address for ethereum network
    :return: public address
    """
    _, addr = address_pk()
    return addr


def r_digital(start: int = 0, end: int = 1000, decimals: int = 0) -> Union[int, float]:
    """
    Generate random digital.
    If you need random float number, you must add decimals attribute
    """
    rand_digital: int = random.randint(start, end)
    if decimals > 0:
        float_str: str = str(random.randint(0, int('9'*decimals)))
        decimals_digit: str = '0.' + '0' * (decimals - len(float_str)) + float_str
        rand_digital += float(decimals_digit)
    return rand_digital


def r_string(length: int = 64, space: bool = False) -> str:
    """
    Generate random string with space or without
    """
    rules: str = string.ascii_letters + ' ' if space else string.ascii_letters
    return ''.join(random.choice(rules) for _ in range(length))


def r_status(statuses=None, status_code: bool = False) -> str:
    """
    Return random status from array
    """
    if statuses is None and not status_code:
        statuses: list = ["complete", "fail", "prepare"]
    elif statuses is None and status_code:
        statuses: list = [200, 201, 400, 404, 500]
    return statuses[random.randint(0, len(statuses))]


def r_phone(f_digital: str = '8') -> str:
    """
    Generate random mobile phone with default start 8
    """
    return f_digital + ''.join(random.choice(string.digits) for _ in range(7))
