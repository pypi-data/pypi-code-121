f = lambda x: isinstance(x, dict)
t = lambda: all([
  not f('abc'),
  not f(''),
  not f(0),
  not f([]),
  not f(['ab','cd']),
  not f([{'a':0},{'b':1}]),
  f({'a':0, 'b':1}),
])
