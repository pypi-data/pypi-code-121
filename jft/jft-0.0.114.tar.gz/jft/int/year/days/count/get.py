from jft.int.year.days.first.get import f as d
f = lambda x: (d(x+1)-d(x)).days
t = lambda: all([f(2022) == 365, f(2020) == 366])
