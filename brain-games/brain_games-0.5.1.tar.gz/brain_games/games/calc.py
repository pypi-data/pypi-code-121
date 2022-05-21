"""Calc game engine."""

import random
from operator import add, mul, sub

GAME_DESCRIPTION = 'What is the result of the expression?'

OPERATIONS = [(add, '+'), (sub, '-'), (mul, '*')]

MIN_NUM = 1
MAX_NUM = 20


def get_challenge():
    """Calc game Q&A generation.

    generate two random numbers
    and calculate result of random operation from list

    Returns:
        question{str} : operation description;
        answer{str} : result of operation
    """
    num1 = random.randint(MIN_NUM, MAX_NUM)
    num2 = random.randint(MIN_NUM, MAX_NUM)
    operation, sign = random.choice(OPERATIONS)
    answer = str(operation(num1, num2))
    question = '{} {} {}'.format(num1, sign, num2)
    return (question, answer)
