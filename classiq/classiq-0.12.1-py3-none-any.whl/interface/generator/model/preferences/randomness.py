import random


def create_random_seed():
    _MIN_SEED = 0
    _MAX_SEED = (
        2**32 - 1
    )  # not certain of underline limitation in minizinc, 32bit should enough
    return random.SystemRandom().randint(a=_MIN_SEED, b=_MAX_SEED)
