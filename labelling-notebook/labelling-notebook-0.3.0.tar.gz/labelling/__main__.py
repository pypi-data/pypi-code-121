import argparse
import os
import logging
import webbrowser

from threading import Timer
from labelling.notebook import create_app

module_dir = os.path.dirname(__file__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default=os.getcwd(),
                        help="root directory for browsing files")

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', default='9888', type=int,
                        help="The port the labelling notebook server will listen on (default=9888)")
    parser.add_argument('--ip', default='127.0.0.1', type=str,
                        help="The IP address the labelling notebook server will listen on (default=127.0.0.1)")
    parser.add_argument('--frontend', default=os.path.join(module_dir, '../frontend/build'),
                        help="frontend built directory")

    args = parser.parse_args()
    run_notebook(args)


def run_notebook(args):
    instant_path = os.path.abspath(args.root)
    app = create_app(
        instance_path=instant_path,
        static_folder=args.frontend,
    )

    Timer(1, lambda: _try_open_browser(args)).start()
    app.run(debug=args.debug, port=args.port, host=args.ip)


def _try_open_browser(args):
    if args.no_browser:
        return

    webbrowser.open_new(f'http://localhost:{args.port}')
