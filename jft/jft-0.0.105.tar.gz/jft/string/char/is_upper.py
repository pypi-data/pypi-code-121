from string import ascii_uppercase
# is_upper
f = lambda α: α in ascii_uppercase
t = lambda: all([
  *[f(_) for _ in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'],
  *[not f(_) for _ in 'abcdefghijklmnopqrstuvwxyz']
])