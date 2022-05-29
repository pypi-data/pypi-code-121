from string import ascii_uppercase
def f(x):
  if x[:4] == 'den ': return True
  return (
    all([
      isinstance(x, str),
      # not (' ' in x and x[:3] != 'El '),
      x[0] in ascii_uppercase]) if len(x)
    else False
  )
t = lambda: all([
  f('Forbes'),
  f('El Sawah'),
  f('den Hartog'),
  f('Hene Kankanamge'),
  not any([f(_) for _ in [
    'apple',
    ''
  ]])
])
