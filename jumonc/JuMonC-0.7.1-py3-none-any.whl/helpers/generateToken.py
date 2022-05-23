from binascii import hexlify
from os import urandom


def generateToken() -> str:
    return hexlify(urandom(24)).decode('ascii')