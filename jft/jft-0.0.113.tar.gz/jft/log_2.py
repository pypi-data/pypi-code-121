from math import log
f = lambda x: log(x, 2)
t = lambda: all([-1 == f(0.5), 0 == f(1), 1 == f(2), 2 == f(4), 3 == f(8)])