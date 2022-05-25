from jft.text_colours.data import RESET
BRIGHT_WHITE = '\033[1;37m'
f = lambda μ: f'{BRIGHT_WHITE}{μ}{RESET}'
t = lambda: '\x1b[1;37mxyz\x1b[0;0m' == f('xyz')