from random import choice, getrandbits, randrange, random
from time import sleep

from .utilities import get_data


def magic_8ball() -> None:
    '''
    Creates a standard Magic 8 Ball game dialog

    Returns:
        None
    '''
    answers = get_data('other', 'magic_8ball_answers')

    def main() -> None:
        input('Ask me a question:\n  ')

        print('Thinking...')
        sleep(randrange(0, 3))

        print(f'  {choice(answers)}\n')

    while True:
        main()
        repeat = input('Would you like to ask another question? [Y/N] ')
        if repeat.upper() != 'Y':
            print('Come back if you have questions.')
            break


def flip_coin() -> int:
    '''
    Returns a random sequence consisting of ASCII symbols and digits
    or a list of a random sequences

    Returns:
        int: 0 or 1 with equal probability (also -1 with chance of 1%)
    '''
    if random() < 0.01:
        return -1
    else:
        return int(getrandbits(1))


if __name__ == '__main__':
    print(flip_coin())
