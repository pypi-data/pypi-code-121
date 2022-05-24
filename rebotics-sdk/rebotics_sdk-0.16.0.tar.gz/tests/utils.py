import random

RANDOM_STRING_SYMBOLS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def get_random_string(length: int, allowed_symbols: str = RANDOM_STRING_SYMBOLS) -> str:
    """
    Return a random string with defined length in the same way as
    django.utils.crypto.get_random_string does.
    But this method is not cryptographically strong, it should not be used anywhere
    outside the tests.
    """
    return ''.join(random.choice(allowed_symbols) for _ in range(length))
