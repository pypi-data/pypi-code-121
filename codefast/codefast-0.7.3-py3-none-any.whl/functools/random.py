import random
import string


def random_string(length: int = 10) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
