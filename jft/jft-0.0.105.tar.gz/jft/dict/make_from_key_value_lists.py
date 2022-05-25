t = lambda: f(list('abc'), [0, 1, 2]) == {'a': 0, 'b': 1, 'c': 2}
f = lambda keys, values: dict(zip(keys, values))