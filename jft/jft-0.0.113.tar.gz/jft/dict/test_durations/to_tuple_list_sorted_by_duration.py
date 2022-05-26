f = lambda x: sorted(list(x.items()), key=lambda x: x[1])
t = lambda: all([[('b.py', 1), ('a.py', 2)] == f({'a.py': 2, 'b.py': 1})])