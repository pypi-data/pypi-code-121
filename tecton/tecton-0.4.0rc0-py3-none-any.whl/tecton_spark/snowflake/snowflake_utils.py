import random
import string


def generate_random_name() -> str:
    return "".join(random.choice(string.ascii_uppercase) for i in range(20))
