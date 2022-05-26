ε = 5e-324
f = lambda: ε
t = lambda: all([f() > 0, f()/f() == 1])
  