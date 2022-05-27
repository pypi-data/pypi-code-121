import random
from . import load_config


def main():
    config = load_config()
    print(f'Goldfish is gladfull for {random.choice(config.nouns)}!')


