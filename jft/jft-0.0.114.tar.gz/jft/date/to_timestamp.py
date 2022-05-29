from datetime import date as d
from datetime import datetime as dt

f = lambda x: dt(x.year, x.month, x.day).timestamp()

t = lambda: all([
  f(d(1970,1,1)) == -36000,
  f(d(1970,1,2)) == 50400,
  f(d(2022,3,4)) == 1646312400
])