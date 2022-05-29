f = lambda line: 'version' in line
t = lambda: all([
  all([f('xyz version'), f('version'), f('version xyz')]),
  not any([f('xyz'), f('')])
])