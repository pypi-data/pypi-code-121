from jft.text_colours.data import RESET
BRIGHT_MAGENTA = '\033[1;35m'
f = lambda μ: f'{BRIGHT_MAGENTA}{μ}{RESET}'
t = lambda: '\x1b[1;35mxyz\x1b[0;0m' == f('xyz')