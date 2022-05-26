f = lambda k: k.replace('\n', '', 1) if k.startswith('\n') else k
t = lambda: all([
  'abc' == f('abc'),
  'abc\nxyz' == f('abc\nxyz'),
  'abc\nxyz' == f('\nabc\nxyz'),
  '\nabc\nxyz' == f('\n\nabc\nxyz'),
])
