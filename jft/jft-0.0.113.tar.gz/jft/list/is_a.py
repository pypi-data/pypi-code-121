f = lambda x: isinstance(x, list)
t = lambda: all([f([]), f(["a"]), f([2, 1]), not any([f(_) for _ in [0, 1.5]])])