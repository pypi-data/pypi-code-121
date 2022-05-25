import random
import string
import uuid


def random_string(length=12, punctuations=False):
    letters = string.ascii_lowercase + string.digits
    if punctuations:
        letters += "!@#$^&"
    return random.SystemRandom().choice(string.ascii_lowercase) + "".join(
        random.SystemRandom().choice(letters) for _ in range(length - 1)
    )


def random_uuid():
    return str(uuid.uuid4())
