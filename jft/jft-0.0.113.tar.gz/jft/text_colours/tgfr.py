from jft.text_colours.success import f as success
from jft.text_colours.danger import f as danger
f = lambda b: (success if b else danger)(f'{str(bool(b)):5}')
t = lambda: all([
  f(1) == '\x1b[1;32mTrue \x1b[0;0m', f(0) == '\x1b[1;31mFalse\x1b[0;0m'
])
