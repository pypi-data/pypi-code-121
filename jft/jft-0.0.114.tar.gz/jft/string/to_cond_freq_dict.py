def f(x):
  d = {}
  for i in range(len(x)-2):
    a, b = x[i]+x[i+1], x[i+2]
    if a not in d: d[a] = {}
    d[a][b] = 1 if b not in d[a] else d[a][b] + 1
  return d

t = lambda: f('James!') == {
  'Ja': {'m': 1},
  'am': {'e': 1},
  'me': {'s': 1},
  'es': {'!': 1}
}