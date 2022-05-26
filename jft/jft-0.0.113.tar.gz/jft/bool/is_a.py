f = lambda x: isinstance(x, bool)
t = lambda: all([f(True), f(False), not any([f(''), f(0), f([])])])