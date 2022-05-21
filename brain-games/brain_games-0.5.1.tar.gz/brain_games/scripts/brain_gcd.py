#!/usr/bin/env python3
"""GCD game script."""

from brain_games.engine import run_game
from brain_games.games import gcd


def main():
    """GCD game script."""
    run_game(gcd)


if __name__ == '__main__':
    main()
