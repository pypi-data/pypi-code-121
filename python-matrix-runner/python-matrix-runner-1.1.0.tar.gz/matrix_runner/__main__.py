# -*- coding: utf-8 -*-

import platform
import os

from argparse import ArgumentParser
from pathlib import Path
from shutil import copyfile

from .inspect import InspectRunner
from .preferences import Preferences


def inspect(_, argv):
    """Inspect script

    Args:
        _: (ignored)
        argv (list): Remaining command line arguments to be passed on
    """
    InspectRunner(argv)


def config(args, _):
    """Configure preferences

    Args:
        args (Namespace): Arguments from the parser
        _: (ignored)
    """
    if args.system:
        name = "system"
        conf = Preferences.system_conf
    if args.user:
        name = "user"
        conf = Preferences.user_conf
    if args.local:
        name = "local"
        conf = Path.cwd().joinpath(Preferences.local_conf.name)
    if not args.action:
        print(f"The {name} config file is located at:")
        print(conf)
    if args.action == "list":
        if conf.exists():
            with open(conf, encoding='utf-8') as file:
                print(file.read())
        else:
            print(f"No {name} config file exists at:")
            print(conf)
    if args.action == "init":
        copyfile(Preferences.system_conf, conf)
    if args.action == "edit":
        if platform.system() == "Windows":
            os.startfile(conf)  # pylint: disable=no-member
        else:
            os.system(f"editor {conf}")


def main():
    """Main function"""
    parser = ArgumentParser(prog='python -m matrix_runner')
    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')

    config_parser = subparsers.add_parser('config', help='Configure matrix-runner preferences')
    group = config_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--system', action='store_true', help="System defaults.")
    group.add_argument('-u', '--user', action='store_true', help="User settings.")
    group.add_argument('-l', '--local', action='store_true', help="Local folder settings.")
    config_parser.add_argument('action', choices=['list', 'init', 'edit'],  nargs='?', help="Action")

    subparsers.add_parser('inspect', help='Inspect a matrix build script')

    args, argv = parser.parse_known_args()

    __import__(__name__).__dict__[args.cmd](args, argv)


main()
