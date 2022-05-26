def f(content):
  while '\n\n\n' in content:
    content = content.replace('\n\n\n', '\n\n')
  return content

t = lambda: all([
  '\n' == f('\n'),
  'a\nz' == f('a\nz'),
  'a\n\nz' == f('a\n\nz'),
  'a\n\nz' == f('a\n\n\nz'),
  'abc' == f('abc'),
])