def f(content):
  while '\n\n' in content:
    content = content.replace('\n\n', '\n')
  return content

t = lambda: all([
  '\n' == f('\n'),
  'a\nz' == f('a\nz'),
  'a\nz' == f('a\n\nz'),
  'a\nz' == f('a\n\n\nz'),
  'abc' == f('abc'),
])