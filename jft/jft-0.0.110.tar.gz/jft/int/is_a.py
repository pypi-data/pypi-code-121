f = lambda x: isinstance(x, int)
t = lambda: all([f(1), not any([f(_) for _ in ['x', [], {}, 0.01]])])