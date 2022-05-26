from jft.text_colours.data import RESET

CYAN = '\033[0;36m'

f = lambda μ: f'{CYAN}{μ}{RESET}'
t = lambda: '\x1b[0;36mxyz\x1b[0;0m' == f('xyz')