from typing import Dict

import cryptography.fernet


def generate_key(hub) -> str:
    key = cryptography.fernet.Fernet.generate_key()
    return key.decode("utf-8")


def encrypt(hub, data: Dict, key: str) -> bytes:
    fernet = cryptography.fernet.Fernet(key)
    raw = hub.crypto.init.dump(data)
    return fernet.encrypt(raw)


def decrypt(hub, data: bytes, key: str) -> Dict:
    fernet = cryptography.fernet.Fernet(key)
    raw = fernet.decrypt(data)
    return hub.crypto.init.load(raw)
