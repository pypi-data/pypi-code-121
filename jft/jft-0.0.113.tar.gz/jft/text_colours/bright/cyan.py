from jft.text_colours.data import RESET
BRIGHT_CYAN = '\033[1;36m'
f = lambda μ: f'{BRIGHT_CYAN}{μ}{RESET}'
t = lambda: '\x1b[1;36mxyz\x1b[0;0m' == f('xyz')