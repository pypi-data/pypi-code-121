f = lambda x: any([
  ' = lambda self' in x,
  ' = lambda:' in x,
  ' = lambda ' in x,
])
t = lambda: all([
  not f('abc'),
  f('abc = lambda self'),
  f('run = lambda:'),
  f('run = lambda '),
  f('test = lambda:'),
  f('test = lambda ')
])
