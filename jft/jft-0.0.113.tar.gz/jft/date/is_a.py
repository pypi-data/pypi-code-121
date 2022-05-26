from datetime import date
f = lambda x: isinstance(x, date)
t = lambda: all([f(date.today()), not any([f(_) for _ in [0, 'abc', 1.5, {}]])])