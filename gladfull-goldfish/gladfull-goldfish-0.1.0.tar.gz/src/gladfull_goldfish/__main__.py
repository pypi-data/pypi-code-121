import random
from . import load_config


def main():
    config = load_config()

    print(f'Goldfish is gladful fo {random.choice(config.nouns)}!')


if __name__ == '__main__':
    main()
