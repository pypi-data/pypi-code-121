f = lambda φ: φ.endswith('.py')
t = lambda: all([not f('abc.txt'), f('foo.py')])