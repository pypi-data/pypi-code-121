"""Prime game engine."""

import random

GAME_DESCRIPTION = 'Answer "yes" if number prime otherwise answer "no".'

MIN_NUM = 1
MAX_NUM = 100


def get_challenge():
    """Prime game Q&A generation.

    generate random Number and check if a Number is Prime

    Returns:
        question{str} : Number;
        answer{str} : Prime status
    """
    num = random.randint(MIN_NUM, MAX_NUM)
    answer = 'yes' if is_prime(num) else 'no'
    question = '{}'.format(num)
    return (question, answer)


def is_prime(num):
    """Prime number check.

    Args:
        num (int): number to check

    Returns:
        bool: True or False
    """
    if num < 2:
        return False
    index = 2
    while index <= num // 2:
        if num % index == 0:
            return False
        index += 1
    return True
