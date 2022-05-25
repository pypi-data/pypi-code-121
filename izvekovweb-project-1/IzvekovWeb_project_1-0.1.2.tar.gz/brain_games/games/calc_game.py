import random


def play_calc_game(name):
    """Brain-calc

        Cуть игры в следующем: пользователю показывается случайное математическое выражение, 
        например 35 + 16, которое нужно вычислить и записать правильный ответ.
    """
    operators = ('+', '-', '*')
    win = 0
    while win < 3:
        rand_values = [random.randint(0, 100), random.randint(0, 100)]
        rand_operation_index = random.randint(0, len(operators) - 1)

        if operators[rand_operation_index] == '+':
            correct_answer = rand_values[0] + rand_values[1]
        elif operators[rand_operation_index] == '-':
            correct_answer = rand_values[0] - rand_values[1]
        elif operators[rand_operation_index] == '*':
            correct_answer = rand_values[0] * rand_values[1]

        print(f'Question: {rand_values[0]} {operators[rand_operation_index]} {rand_values[1]}')
        answer = input('Your answer: ')

        def is_int(str):
            try:
                int(str)
                return True
            except ValueError:
                return False

        if not is_int(answer) or int(answer) != correct_answer:
            print(f"'{answer}' is wrong answer ;(. Correct answer was '{correct_answer}'.\n \
                Let's try again, {name}!")
            break
        else:
            print('Correct!')
            win += 1
        if win == 3:
            print(f'Congratulations, {name}!')
