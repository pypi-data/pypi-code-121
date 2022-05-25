from random import random


def play_even_game(name):
    """Brain-even

        Answer "yes" if the number is even, otherwise answer "no".
    """

    print('Answer "yes" if the number is even, otherwise answer "no".')

    win = 0
    while win < 3:
        rand_int = int(random() * 100)
        correct_answer = 'yes' if rand_int % 2 == 0 else 'no'
        print(f'Question: {rand_int}')
        answer = input('Your answer: ')
        if answer != correct_answer:
            print(f"'{answer}' is wrong answer ;(. Correct answer was '{correct_answer}'.\n \
                Let's try again, {name}!")
            break
        else:
            print('Correct!')
            win += 1
        if win == 3:
            print(f'Congratulations, {name}!')
