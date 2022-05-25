from brain_games.cli import welcome_user
from brain_games.games.calc_game import play_calc_game


def main():
    """Brain-even main"""

    user_name = welcome_user()
    play_calc_game(user_name)


if __name__ == '__main__':
    main()
