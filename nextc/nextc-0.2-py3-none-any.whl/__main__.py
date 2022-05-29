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
import sys

import click
import llvmlite
import rply

from . import __version__
from .lexing import Tokenizer


# TODO: Compile Command
@click.group()
@click.version_option(
    __version__,
    '--version',
    '-v',
    message=f'nextc: %(version)s\nllvmlite: {llvmlite.__version__}\nrply: {rply.__version__}\nclick: {click.__version__}\npython: {sys.version}',
)
def cli():
    pass


@cli.command('lex')
@click.option('-f', '--file', 'file', required=True, help='The File to Lex')
def lex_code(file: str):
    with open(file) as f:
        buffer = f.read()
        tokenizer = Tokenizer(code=buffer, filename=file)
        tokens = tokenizer.start()
        print(str(tokens), file=sys.stderr)


if __name__ == '__main__':
    cli()
