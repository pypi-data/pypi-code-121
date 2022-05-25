def f(x):
  for (before, after) in [
    ('\n_', '\n\n_'),
    ('\nc', '\n\nc'),
    ('\ne', '\n\ne'),
    ('\na', '\n\na'),
  ]:
    x = x.replace(before, after)
  return x

t = lambda: all([
  '\n\n_' == f('\n_'), 
  '\n\nc' == f('\nc'), 
  '\n\ne' == f('\ne'), 
  '\n\na' == f('\na'), 
])