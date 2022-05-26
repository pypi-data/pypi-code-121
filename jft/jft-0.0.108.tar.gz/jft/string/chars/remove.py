from string import ascii_letters as _L
from string import digits as _D

f = lambda x: (
  ''.join([ch for ch in x['str'] if ch not in x['chars']])
  if all([k in x.keys() for k in ['str', 'chars']]) else ''
)

t = lambda: all([
  f({'str': 'abc', 'chars': 'ab'}) == 'c',
  f({'str': 'abcdefghijklm', 'chars': 'aeiou'}) == 'bcdfghjklm',
  f({'str': 'abc1234567klm', 'chars': '0123456789'}) == 'abcklm',
  f({'str': 'abc!ABC123', 'chars': _L}) == '!123',
  f({'str': 'abc!ABC123', 'chars': _D}) == 'abc!ABC',
  f({'str': 'abc!ABC123', 'chars': _L+_D}) == '!',
])
