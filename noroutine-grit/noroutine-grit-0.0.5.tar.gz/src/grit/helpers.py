import string
import random

def gen_random_str(length: int = 16):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=length))