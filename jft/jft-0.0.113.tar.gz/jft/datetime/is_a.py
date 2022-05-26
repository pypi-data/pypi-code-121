from datetime import datetime
f = lambda x: isinstance(x, datetime)
t = lambda: all([f(datetime.now()), not any([f(_) for _ in [0, 'abc', 1.5]])])