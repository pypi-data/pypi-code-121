from jft.text_colours.data import RESET
YELLOW = '\033[0;33m'
f = lambda μ: f'{YELLOW}{μ}{RESET}'
t = lambda: '\x1b[0;33mxyz\x1b[0;0m' == f('xyz')