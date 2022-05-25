from jft.text_colours.data import RESET
WHITE = '\033[0;37m'
f = lambda μ: f'{WHITE}{μ}{RESET}'
t = lambda: '\x1b[0;37mxyz\x1b[0;0m' == f('xyz')