from datetime import date
def f(x):
  if '-' in x: char = '-'
  if '/' in x: char = '/'
  return date(*[int(_) for _ in x.split(char)])

t = lambda: all([
  f('2000-01-31') == date(2000, 1, 31),
  f('2000/01/31') == date(2000, 1, 31)
])