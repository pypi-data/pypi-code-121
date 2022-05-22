"""
cli entrypoint

Usage:
    cdcli [<n>]
    cdcli [<n>] -f <training_file_path>

Options:
    -h --help       Show this screen.

"""
import sys, os
import time
import json
import random
from docopt import docopt

from clichessdrill.game import Game
from clichessdrill.pieces import Pieces

DEFAULT_GAME_PLAN = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'gameplans', 'daniel-01.json')

random.seed(int(time.time()))


def main():

    arguments = docopt(__doc__)
    print(arguments)

    n_rounds = arguments.get('<n>')
    n_rounds = 1 if n_rounds is None else n_rounds
    try:
        n_rounds = int(n_rounds)
    except TypeError:
        message = f'Number of rounds n must be an integer. Value provided: {n_rounds}'
        print(message)
        sys.exit(0)

    if arguments['-f']:
        training_file_path = arguments['<training_file_path>']
    else:
        training_file_path = DEFAULT_GAME_PLAN

    print(f'using training file: {training_file_path}')

    with open(training_file_path) as f:
        plan = json.loads(f.read())

    for i in range(n_rounds):
        user_pieces = random.choice([Pieces.WHITE, Pieces.BLACK])
        game = Game(plan=plan, user_pieces=user_pieces)
        game.run()
        time.sleep(1)
