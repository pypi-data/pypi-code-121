f = lambda x: isinstance(x, float)
t = lambda: all([f(0.01), not any([f(_) for _ in ['x', [], {}, 1]])])