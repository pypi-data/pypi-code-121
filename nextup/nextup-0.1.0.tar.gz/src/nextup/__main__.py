# MIT License
#
# Copyright (c) 2022 Venera Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import sys

import click


MODULES = [
    'nextc',
    'parcel'
]


@click.group()
@click.version_option(
    None,
    '--version',
    '-v',
    message=f'nextup: %(version)s',
)
def cli():
    pass


@cli.command('module-add')
@click.argument('module')
def add_module(module: str):
    if module not in MODULES:
        return print('ERROR: Invalid Module Name', file=sys.stderr)

    os.system(f'pip install {module}')

    click.echo(f'Successfully Installed {module}')


@cli.command('module-update')
@click.argument('module')
def update_module(module: str):
    if module not in MODULES:
        return print('ERROR: Invalid Module Name', file=sys.stderr)

    os.system(f'pip install -U {module}')

    click.echo(f'Successfully Updated {module}')


@cli.command('update')
def update():
    os.system('pip install -U nextup')


if __name__ == '__main__':
    cli()
