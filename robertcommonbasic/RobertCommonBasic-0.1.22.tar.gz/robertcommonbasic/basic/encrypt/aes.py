from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

def add_to_16_key(secret: str) -> bytes:
    return f"{secret}_robert@20220119"[0:16].encode('utf-8')

def aes_encrypt(content: bytes, secret: str='') -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(add_to_16_key(secret), AES.MODE_CFB, iv)
    return iv + cipher.encrypt(content)

def aes_decrypt(content: bytes, secret: str='') -> bytes:
    iv = content[:16]
    cipher = AES.new(add_to_16_key(secret), AES.MODE_CFB, iv)
    return cipher.decrypt(content[16:])