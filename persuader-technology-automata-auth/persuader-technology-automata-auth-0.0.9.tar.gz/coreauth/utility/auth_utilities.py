import hashlib
import hmac
import time


def get_timestamp():
    return int(time.time() * 1000)


def sign_value_with_secret(value, secret):
    return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
