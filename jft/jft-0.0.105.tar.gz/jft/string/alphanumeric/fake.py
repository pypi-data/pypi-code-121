from random import choice
from string import ascii_letters as _l
from string import digits as _d

chars = _l + _d

f = lambda x: ''.join([choice(chars) for _ in range(x)])

t = lambda: all([
  *[len(f(x)) == x for x in range(10)],
  *[char in chars for char in f(26)]
])
