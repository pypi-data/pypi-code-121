from jft.text_colours.data import RESET
BRIGHT_GREEN = '\033[1;32m'
f = lambda μ: f'{BRIGHT_GREEN}{μ}{RESET}'
t = lambda: '\x1b[1;32mxyz\x1b[0;0m' == f('xyz')