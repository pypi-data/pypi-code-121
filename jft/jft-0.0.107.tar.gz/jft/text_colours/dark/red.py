from jft.text_colours.data import RESET
RED = '\033[0;31m'
f = lambda μ: f'{RED}{μ}{RESET}'
t = lambda: '\x1b[0;31mxyz\x1b[0;0m' == f('xyz')
