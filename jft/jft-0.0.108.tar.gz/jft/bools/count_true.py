f = lambda x: len([_ for _ in x if _])
t = lambda: all([
  3 == f([True, True, True, False]),
  2 == f([1, 1, 0, False]),
  0 == f([])
])
