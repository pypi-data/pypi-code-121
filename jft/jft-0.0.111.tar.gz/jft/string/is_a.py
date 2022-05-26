f = lambda x: isinstance(x, str)
t = lambda: all([f(""), f("a"), not any([f(_) for _ in [0, 1.5]])])