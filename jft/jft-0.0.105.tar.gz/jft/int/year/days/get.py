from datetime import date as dt
from datetime import timedelta as td
from jft.int.year.days.first.get import f as d

f = lambda x:[_ for _ in [d(x) + td(days=δ) for δ in range(367)] if _ < d(x+1)]

t = lambda: f(2022) == sorted([
  *[dt(2022, m, _) for _ in range(1, 32) for m in [1, 3, 5, 7, 8, 10, 12]],
  *[dt(2022, m, _) for _ in range(1, 31) for m in [4, 6, 9, 11]],
  *[dt(2022, 2, _) for _ in range(1, 29)],
])