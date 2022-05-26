f = lambda text: text.find('(')
t = lambda: all([-1 == f('abc'), 3 == f('abc('), 3 == f('abc((')])
