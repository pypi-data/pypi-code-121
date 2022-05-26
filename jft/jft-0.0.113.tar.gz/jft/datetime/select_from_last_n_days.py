from datetime import datetime as dt
from datetime import timedelta as td
from random import uniform

f = lambda x: dt.now() - td(days=uniform(0, x))

t = lambda: all([
  all([(dt.now() - f(max_days)) < td(days=max_days) for _ in range(10)])
  for max_days in range(90, 100)
])
