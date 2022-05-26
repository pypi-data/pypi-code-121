f = lambda x: isinstance(x, set)
t = lambda: all([f(set()), f({"a"}), f({2, 1}), not any([f(''), f(0), f([])])])