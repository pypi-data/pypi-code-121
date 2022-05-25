from datetime import date as d

def f(day, period): return period[0] <= day <= period[1]

def t(): return all([
  f(d(2022,1,1), (d(2022,1,1), d(2022,1,31))),
  f(d(2022,1,15), (d(2022,1,1), d(2022,1,31))),
  f(d(2022,1,31), (d(2022,1,1), d(2022,1,31))),
  not f(d(2022,1,15), (d(2022,2,1), d(2022,1,31)))
])