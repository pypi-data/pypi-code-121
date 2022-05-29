from datetime import date as d
from datetime import timedelta as td
from random import randint

f = lambda x: d.today() - td(days=randint(0, x))

def t():
  d_0 = d.today()
  f_1, f_2 = f(1), f(2)
  a = f(0) == d_0
  b = any([f_1 == d_0, f_1 == d_0-td(days=1)]) 
  c = any([f_2 == d_0, f_2 == d_0-td(days=1), f_2 == d_0-td(days=2)])
  return all([all([a, b, c]) for _ in range(1000)])
