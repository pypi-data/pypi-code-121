_file_a = lambda x: ('\n' if '\n' in x else '') + f'{x}'
max_length = 24*450

def f(x):
  result = _file_a(x)
  if len(result) > max_length:
    result = result[:max_length] + '...'
  return result

t = lambda: all([
  expectation == observation
  for (expectation, observation)
  in [
    ('a'*max_length + '...', f('a'*(max_length+1))),
    ('a'*(max_length-1), f('a'*(max_length-1))),
    ('a'*max_length, f('a'*(max_length))),
  ]
])
