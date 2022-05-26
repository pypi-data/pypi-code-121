#!/usr/bin/env python3

_REQUIRED_EXECUTABLES = [
    'git',
    'mongo',
    'npm',
    'node',
    'nodemon',
    'ts-node'
]

_MISSING_EXECUTABLE_ERROR = """The following executables are required to be accessible through $PATH in order to run this program: {}
The following one is missing: {}
"""

class MissingExecutableException(Exception):
    def __init__(self, missing:str):
        self.missing = missing
    def __str__(self):
        return _MISSING_EXECUTABLE_ERROR.format(
            ' '.join(_REQUIRED_EXECUTABLES),
            self.missing
        )


if __name__ == '__main__':
    import shutil
    import sys
    import argparse

    try:
        for n in _REQUIRED_EXECUTABLES:
            if shutil.which(n) is None:
                raise MissingExecutableException(n)
    except MissingExecutableException as e:
        print(e)
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Savitrigen')
    parser.add_argument('-l', '--list-presets', action='store_true', help='lists available presets then exits')
    parser.add_argument('-p', '--preset', help='creates briefing.yml from a preset then exits')
    parser.add_argument('-v', '--version', action='store_true', help='displays version then exits')

    args = parser.parse_args()

    from savitrigen.commandline import main, preset, list_presets, print_version
    from savitrigen.userdir import make_userdir

    make_userdir()
    match args.preset:
        case str(): preset(args.preset)
        case None if args.list_presets: list_presets()
        case None if args.version: print_version()
        case None: main()
