from jft.text_colours.data import RESET
MAGENTA = '\033[0;35m'
f = lambda μ: f'{MAGENTA}{μ}{RESET}'
t = lambda: '\x1b[0;35mxyz\x1b[0;0m' == f('xyz')