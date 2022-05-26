f = lambda x, y: (len(y) - len(y.replace(x, '')))//len(x)
t = lambda: 4 == f('ow', 'How Now Brown Cow')
