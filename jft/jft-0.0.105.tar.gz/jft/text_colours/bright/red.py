from jft.text_colours.data import RESET
BRIGHT_RED = '\033[1;31m'
f = lambda μ: f'{BRIGHT_RED}{μ}{RESET}'
t = lambda: '\x1b[1;31mxyz\x1b[0;0m' == f('xyz')