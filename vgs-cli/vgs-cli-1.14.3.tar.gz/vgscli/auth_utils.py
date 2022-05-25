import random
import string
import hashlib
import base64


def generate_code_verifier(stringLength=64):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def code_challenge(code_verifier):
    sha_signature = __sha256(code_verifier.encode())
    return __base64_url_encode(sha_signature).decode('UTF-8').split('=')[0]


def __sha256(buffer):
    m = hashlib.sha256()
    m.update(buffer)
    return m.digest()


def __base64_url_encode(random_bytes):
    return base64.urlsafe_b64encode(random_bytes)


