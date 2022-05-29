from json import loads
from json import dumps

def f(x):
  try:
    loads(x)
  except ValueError:
    return False
  return True

t = lambda: all([not f(''), f(dumps({'a': 0, 'b': 1}))])