import secrets 
from html import entities
from bcrypt import hashpw, gensalt, checkpw
from random import randint

from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def secure_password(password):
    password_hashed = hashpw(password.encode('utf-8'), gensalt())
    try: #todo: remove
        password_hashed = password_hashed.decode('utf-8')
    except:
        pass
    return password_hashed

def compare_passwords(password,hash_saved):
    valid = checkpw(str(password).encode('utf-8'),str(hash_saved).encode('utf-8'))
    return valid

def get_token():
    return secrets.token_urlsafe(45)

def get_keys_numbers(key):
    key_numbers  = [ord(x) for x in key]
    keys_numbers = [x for x in str(sum(key_numbers))[:3]]
    return keys_numbers

def magic_code(key):
    keys_numbers    = get_keys_numbers(key)
    
    values          = [str(randint(100, 999)) + x for x in keys_numbers]
    
    completes       = []
    for value in values[1:]:
        completes.append(''.join([str(9 - int(x)) for x in value]))
    values.extend(completes)
    return '-'.join([str(x) for x in values])
    
def check_magic_code(code,key):
    numbers = code.split('-')
    if len(numbers) != 5: 
        return False
    try:
        numbers = [int(x) for x in numbers]
    except:
        return False
    first = numbers[0]
    summed = sum(numbers)
    operation_valid = first - 2 == int(str(summed)[1:])
    
    keys_numbers = get_keys_numbers(key)
    sequence = [str(numbers[0])[-1], str(numbers[1])[-1], str(numbers[2])[-1]]
    
    return operation_valid and keys_numbers == sequence

backend = default_backend()
iterations = 100_000

def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))

def password_encrypt(message: str | bytes, password: str, iterations: int = iterations) -> str:
    if type(message) == str:
        message = message.encode("utf-8")
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return (b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )).decode('utf-8')
    )

def password_decrypt(token: str | bytes, password: str) -> bytes:
    if type(token) == bytes:
        token = token.decode("utf-8")
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token).decode('utf-8')