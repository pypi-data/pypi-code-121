from jft.text_colours.data import RESET
BRIGHT_BLUE = '\033[1;34m'
f = lambda μ: f'{BRIGHT_BLUE}{μ}{RESET}'
t = lambda: '\x1b[1;34mxyz\x1b[0;0m' == f('xyz')