import os
from argparse import ArgumentError
from subprocess import CalledProcessError

import sys

from polidoro_argument import PolidoroArgumentParser
from polidoro_cli import CLI_DIR, VERSION, CLI, get_cli, load_clis


def main():
    try:
        # Load CLIs
        load_clis(CLI_DIR)
        if len(sys.argv) == 3 and sys.argv[2] == '--help':
            cli = get_cli(sys.argv[1])
            if cli:
                default_cmd = cli.get_default_command()
                if default_cmd:
                    CLI.execute(f'{default_cmd} --help')

        parser = PolidoroArgumentParser(version=VERSION, prog='cli', raise_argument_error=True)
        try:
            parser.parse_args().positional
        except (ArgumentError, AttributeError) as err:
            sys.argv.insert(2, 'default_command')
            try:
                parser.parse_args()
            except ArgumentError:
                parser.error(str(err))
    except CalledProcessError as error:
        return error.returncode
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    os.environ['CLI_PATH'] = os.path.dirname(os.path.realpath(__file__))

    main()
