f = lambda x: any([_ in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for _ in x])
t = lambda: all([not f(''), not f('abc'), f('ABC'), f('aBc'), ])
