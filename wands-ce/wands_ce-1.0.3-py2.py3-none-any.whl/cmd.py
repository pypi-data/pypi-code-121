# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 15:39
"""
import argparse

parser = argparse.ArgumentParser(description="")

parser.add_argument('-v', '--version', action='version',
                    version='1.0.3', help='version of wands')

subparsers = parser.add_subparsers(
    dest='command', title='Available commands', metavar='')

# runserver
parser_runserver = subparsers.add_parser("runserver")
parser_runserver.add_argument("--host", type=str)
parser_runserver.add_argument("--port", type=int)


def cmd():
    args = parser.parse_args()
    command = args.command
    if command == 'runserver':
        from wands.server.manage import manage
        manage(args.host, args.port)


if __name__ == '__main__':
    cmd()
