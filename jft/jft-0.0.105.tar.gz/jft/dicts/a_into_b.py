f = lambda a, b: {k: a[k] if k in a else b[k] for k in set(a) | set(b)}
t = lambda: f({'u': 0, 'v': 1}, {'v': 2, 'w': 3}) == {'u': 0, 'v': 1, 'w': 3}
