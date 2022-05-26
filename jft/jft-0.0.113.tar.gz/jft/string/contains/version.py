f = lambda x: 'version' in x
t = lambda: all([f('version'), not f('xyz')])