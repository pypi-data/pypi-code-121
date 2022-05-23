from typing import Dict


def sig_generate_key(hub) -> str:
    ...


def sig_encrypt(hub, data: Dict, key: str) -> bytes:
    """
    Returns the encrypted data and the encryption key
    """


def sig_decrypt(hub, data: bytes, key: str) -> Dict:
    ...
