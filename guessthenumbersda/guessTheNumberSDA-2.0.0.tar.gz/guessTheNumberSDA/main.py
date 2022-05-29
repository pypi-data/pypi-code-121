from guessTheNumberSDA.guess_game import start_game
from guessTheNumberSDA.guess_game import validate_input


def play_guess_game():
    credit = validate_input('credit')

    while credit > 5:
        risk = validate_input('risk')
        user_number = validate_input('number to guess')
        credit = start_game(credit, risk, user_number)

if __name__ == '__main__':
    play_guess_game()