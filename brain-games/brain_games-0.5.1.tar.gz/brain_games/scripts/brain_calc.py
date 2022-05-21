#!/usr/bin/env python3
"""Calc game script."""

from brain_games.engine import run_game
from brain_games.games import calc


def main():
    """Calc game script."""
    run_game(calc)


if __name__ == '__main__':
    main()
