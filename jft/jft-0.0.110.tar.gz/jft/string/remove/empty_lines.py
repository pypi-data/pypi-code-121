f = lambda text: text.replace('\n\n\n', '\n\n')
t = lambda: all([
  'abc\n\nxyz' == f('abc\n\n\nxyz'),
  'abc\n\nxyz' == f('abc\n\nxyz'),
  'abc' == f('abc')
])