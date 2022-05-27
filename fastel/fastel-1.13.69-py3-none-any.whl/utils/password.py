import base64
import hashlib
import os


def _encrypt(salt: bytes, password: str) -> bytes:
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt + key


def password_encode(password: str) -> str:
    salt = os.urandom(32)
    password_encoded = _encrypt(salt=salt, password=password)
    stored_password = base64.b64encode(password_encoded).decode()
    return stored_password


def password_verify(stored: str, password: str) -> bool:
    stored_password = base64.b64decode(stored.encode())
    salt = stored_password[:32]
    val_password = _encrypt(salt, password)
    return bool(stored_password == val_password)
