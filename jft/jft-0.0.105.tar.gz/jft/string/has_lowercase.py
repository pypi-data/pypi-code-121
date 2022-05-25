f = lambda x: any([_ in 'abcdefghijklmnopqrstuvwxyz' for _ in x])
t = lambda: all([not f(''), not f('ABC'), f('ABCd'), f('abc')])
