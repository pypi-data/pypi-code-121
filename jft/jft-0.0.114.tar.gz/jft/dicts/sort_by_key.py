f = lambda list, key: sorted(list, key=lambda d: d[key])
t = lambda: all([
  f([{'a': 1, 'z': 1}, {'a': 2, 'z': 0}, {'a': 0, 'z': 2}], 'a')
  ==[{'a': 0, 'z': 2}, {'a': 1, 'z': 1}, {'a': 2, 'z': 0}]
])
