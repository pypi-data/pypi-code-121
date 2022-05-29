f = lambda x: isinstance(x, bool) or x is None
t = lambda: all([not f('a'), not f(0), not f(1), f(True), f(False), f(None)])
