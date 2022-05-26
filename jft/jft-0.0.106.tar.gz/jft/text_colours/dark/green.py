from jft.text_colours.data import RESET
GREEN = '\033[0;32m'
f = lambda μ: f'{GREEN}{μ}{RESET}'
t = lambda: '\x1b[0;32mxyz\x1b[0;0m' == f('xyz')