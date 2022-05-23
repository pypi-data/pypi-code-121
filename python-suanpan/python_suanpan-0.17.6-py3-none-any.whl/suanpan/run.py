# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import copy
import faulthandler
import os
import sys

from suanpan.imports import imports
from suanpan.utils import env as spenv
from suanpan.helper import init_project


def run(component, *args, **kwargs):
    if isinstance(component, str):
        if os.sep in component:
            component = component.lstrip(f'.{os.sep}')

        component = f"{component[:-3]}.app" if component.endswith(".py") else component
        component = imports(component)
    with env(**kwargs.pop("env", {})):
        return component.start(*args, **kwargs)


@contextlib.contextmanager
def env(**kwargs):
    old = copy.deepcopy(spenv.environ)
    spenv.update(kwargs)
    yield spenv.environ
    spenv.update(old)


def cli():
    sys.path.append(os.path.abspath(os.curdir))
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


def helper():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True, title='subcommands',
                                       help='suanpan helper command')
    parser_init = subparsers.add_parser('init')
    parser_init.add_argument('project', nargs='?', type=str, help='new component name')
    parser_init.add_argument('-f', '--format', choices=['normal', 'function', 'autoload'], default='normal',
                             help='init component with code format')
    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('component', help='component name')

    args, _rest = parser.parse_known_args()
    if args.command == 'init':
        init_project(args.project, args.format)
    else:
        sys.path.append(os.path.abspath(os.curdir))
        return run(args.component, *_rest)


if __name__ == "__main__":
    faulthandler.enable()
    cli()
