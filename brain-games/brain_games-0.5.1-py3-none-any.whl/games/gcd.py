"""GCD game engine."""

import random

GAME_DESCRIPTION = 'Find the greatest common divisor of given numbers.'

MIN_NUM = 1
MAX_NUM = 100


def get_challenge():
    """GCD game Q&A generation.

    generate two random Numbers
    and calculate greatest common divider for them

    Returns:
        question{str} : Numbers;
        answer{str} : greatest common divider
    """
    num1 = random.randint(MIN_NUM, MAX_NUM)
    num2 = random.randint(MIN_NUM, MAX_NUM)
    answer = str(gcd(num1, num2))
    question = '{} {}'.format(num1, num2)
    return (question, answer)


def gcd(num1, num2):
    """Find greater common divider.

    Find greater common divider
    for two integer numbers

    Args:
        num1 (int): number one
        num2 (int): number two

    Returns:
        int: Greater Common Divider
    """
    while num1 != num2:
        if num1 > num2:
            num1 -= num2
        else:
            num2 -= num1
    return (num1)
