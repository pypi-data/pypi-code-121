from brain_games.is_int import is_int
import random


def play_gcd_game(name):
    """Game-gcd

        Суть игры в следующем: пользователю показывается два случайных числа,
        например, 25 50. Пользователь должен вычислить и ввести наибольший
        общий делитель этих чисел.
    """
    win = 0
    while win < 3:
        rand_values = [random.randint(0, 100), random.randint(0, 100)]

        print('Find the greatest common divisor of given numbers.')
        print(f'Question: {rand_values[0]} {rand_values[1]}')
        answer = input('Your answer: ')

        correct_answer = find_nod(rand_values[0], rand_values[1])

        if not is_int(answer) or int(answer) != correct_answer:
            print(f"'{answer}' is wrong answer ;(. Correct answer was '{correct_answer}'.\n \
                Let's try again, {name}!")
            break
        else:
            print('Correct!')
            win += 1
        if win == 3:
            print(f'Congratulations, {name}!')


def find_nod(x, y):
    while y > 0:
        z = y
        y = x % y
        x = z
    return x
