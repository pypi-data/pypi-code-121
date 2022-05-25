f = lambda x: not isinstance(x, float)
t = lambda: all([*[f(_) for _ in ['x', [], {}, 1]], not f(0.01)])