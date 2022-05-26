from jft.string.chars.remove import f as remove_chars
from string import ascii_letters as _L
from string import digits as _D
f = lambda x: len(remove_chars({'str': x, 'chars': _L + _D})) > 0
t = lambda: all([not f(''), not f('abcABC123'), f('abc!ABC123')])