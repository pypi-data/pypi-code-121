import argparse
import os
import sys

import bjoern

from .app import create_app
from .errors import MockerinhoError


def get_default_simulations_directory_path() -> str:
    directory = 'simulations/'
    cwd = os.path.abspath(os.getcwd())
    path = os.path.join(cwd, directory)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='mockerinho',
        description='Simulate Web APIs for development and testing purposes.',
    )

    parser.add_argument('-H', '--host',
                        help='specify server`s host', type=str, default='0.0.0.0')
    parser.add_argument('-p', '--port',
                        help='specify server`s port', type=int, default=8000)
    parser.add_argument('-D', '--directory',
                        help='specify simulations directory',
                        type=str,
                        default=get_default_simulations_directory_path())

    return parser.parse_args()


STARTING_SERVER_MESSAGE = '''
Starting Mockerinho server at http://{}:{}
Quit the server with CONTROL-C.'''

SERVER_HAS_STOPPED_MESSAGE = 'Mockerinho server has stopped.'


def main() -> None:
    args = parse_args()
    host, port, directory = args.host, args.port, args.directory

    try:
        app = create_app(directory)
    except MockerinhoError as err:
        message = f'{err}\n'
        sys.stderr.write(message)
        exit(1)

    try:
        print(STARTING_SERVER_MESSAGE.format(host, port))
        bjoern.run(app, host, port)
    except KeyboardInterrupt:
        print(SERVER_HAS_STOPPED_MESSAGE)
