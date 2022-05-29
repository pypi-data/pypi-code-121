from jft.text_colours.data import RESET
BRIGHT_YELLOW = '\033[1;33m'
f = lambda μ: f'{BRIGHT_YELLOW}{μ}{RESET}'
t = lambda: '\x1b[1;33mxyz\x1b[0;0m' == f('xyz')