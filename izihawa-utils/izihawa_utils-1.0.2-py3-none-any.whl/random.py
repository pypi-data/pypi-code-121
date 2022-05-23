import random
import string


def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_request_id(length: int = 12):
    return random_string(length)
