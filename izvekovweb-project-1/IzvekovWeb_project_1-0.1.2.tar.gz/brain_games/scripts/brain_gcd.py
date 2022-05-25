from brain_games.cli import welcome_user
from brain_games.games.gcd_game import play_gcd_game


def main():
    """Brain-even main"""

    user_name = welcome_user()
    play_gcd_game(user_name)


if __name__ == '__main__':
    main()
