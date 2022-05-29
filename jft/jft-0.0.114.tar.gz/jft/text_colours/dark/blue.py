from jft.text_colours.data import RESET
BLUE = '\033[0;34m'
f = lambda μ: f'{BLUE}{μ}{RESET}'
t = lambda: '\x1b[0;34mxyz\x1b[0;0m' == f('xyz')
