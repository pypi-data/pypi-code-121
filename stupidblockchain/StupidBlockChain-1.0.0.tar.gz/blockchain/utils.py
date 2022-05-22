from hashlib import sha256


def hexdigest(data: bytes) -> str:
    return sha256(data).hexdigest()


def digest(data: bytes) -> bytes:
    return sha256(data).digest()


def is_hash_proofed(hash: bytes, difficulty: int, preffix: str) -> bool:
    return hash.hex().startswith(preffix * difficulty)
