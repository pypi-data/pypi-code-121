f = lambda x: any([_ in '0123456789' for _ in x])
t = lambda: all([not f('abyz'), f('ab1yz'), f('ab2yz'), f('ab3yz'), f('ab4yz')])
