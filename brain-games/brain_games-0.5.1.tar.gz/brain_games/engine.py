"""Brain Games Engine."""

import prompt

NUMBER_OF_STEPS = 3


def run_game(game):
    """Brain Games Engine.

    Executing game process

    Args:
        game (function): create game question and answer
    """
    print('Welcome to the Brain Games!\n{}\n'.format(game.GAME_DESCRIPTION))
    user_name = prompt.string('May I have your name? ')
    print('Hello, {}!\n'.format(user_name))
    for step in range(NUMBER_OF_STEPS):
        (game_question, game_answer) = game.get_challenge()
        user_answer = prompt.string(
            'Question: {}\nYour answer: '.format(game_question))
        if user_answer != game_answer:
            print("'{}' is wrong answer ;(. Correct answer was '{}'.".format(
                user_answer, game_answer))
            print("Let's try again, {}!".format(user_name))
            return
        print('Correct!')
    print('Congratulations, {}'.format(user_name))
