from string import ascii_uppercase
f = lambda x: all([
  isinstance(x, str),
  # ' ' not in x,
  x[0] in ascii_uppercase if len(x)
  else False
])
t = lambda: all([
  f('Forbes'),
  f('Michael'),
  f('Talluru Murali'),
  not any([f(_) for _ in [
    # 'New York',
    'apple',
    ''
  ]])
])
