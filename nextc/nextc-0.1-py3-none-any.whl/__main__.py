import sys

import click
import llvmlite
import rply

from . import __version__

# TODO: Compile Command
@click.group()
@click.version_option(
    __version__,
    '--version',
    '-v',
    message=f'nextc: %(version)s\nllvmlite: {llvmlite.__version__}\nrply: {rply.__version__}\npython: {sys.version}',
)
def version():
    pass


if __name__ == '__main__':
    version()
