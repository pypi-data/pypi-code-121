f = lambda x: len(x) - len(x.replace(' ', ''))
t = lambda: all([f('a') == 0, f('a b') == 1, f('a b c') == 2])
