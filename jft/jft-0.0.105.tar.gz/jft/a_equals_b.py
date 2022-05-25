f = lambda a, b: a==b
t = lambda: all([
  all([f(0,0), f(1,1), f('a','a'), f(-1,-1)]),
  not any([f(0,1), f(1,0), f('a','b'), f(-1,1)])
])