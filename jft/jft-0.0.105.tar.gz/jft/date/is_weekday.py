from datetime import date

f = lambda x: x.weekday() < 5
t = lambda: all([
  not any([
    f(date(2022, 12, 31)), # 2022-12-31 5  Saturday
    f(date(2023,  1,  1)), # 2023-01-01 6  Sunday
  ]),
  f(date(2022, 12, 26)),   # 2022-12-26 0  Monday
  f(date(2022, 12, 27)),   # 2022-12-27 1  Tuesday
  f(date(2022, 12, 28)),   # 2022-12-28 2  Wednesday
  f(date(2022, 12, 29)),   # 2022-12-29 3  Thursday
  f(date(2022, 12, 30)),   # 2022-12-30 4  Friday
])