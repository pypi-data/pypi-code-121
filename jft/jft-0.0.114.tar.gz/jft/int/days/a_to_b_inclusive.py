from datetime import date as d
from datetime import timedelta as td

f = lambda a, b: ((b - a) + td(days=1)).days

t = lambda: all([
  f(d(2022, 1, 1), d(2022, 1, 1)) == 1,
  f(d(2022, 1, 1), d(2022, 12, 31)) == 365,
])