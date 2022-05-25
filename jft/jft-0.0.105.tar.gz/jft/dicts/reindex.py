from random import randint as u

def f(dicts, index_name):
  for index, item in enumerate(dicts):
    item[index_name] = index
  return dicts

t = lambda: all([
  f([{'i': 9, 'z': 2}, {'i': 0, 'z': 1}, {'i': 5, 'z': 0}], 'i')
  ==[{'i': 0, 'z': 2}, {'i': 1, 'z': 1}, {'i': 2, 'z': 0}]
])
