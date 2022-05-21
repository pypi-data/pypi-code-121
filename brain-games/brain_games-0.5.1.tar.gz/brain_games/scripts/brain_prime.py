#!/usr/bin/env python3
"""Prime game script."""

from brain_games.engine import run_game
from brain_games.games import prime


def main():
    """Prime game script."""
    run_game(prime)


if __name__ == '__main__':
    main()
