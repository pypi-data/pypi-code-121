from jft.text_colours.data import RESET
DEFAULT = '\033[0;39m'
f = lambda μ: f'{DEFAULT}{μ}{RESET}'
t = lambda: '\x1b[0;39mxyz\x1b[0;0m' == f('xyz')