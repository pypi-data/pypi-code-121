from datetime import datetime
f = lambda x: isinstance(x, datetime)
t = lambda: all([f(datetime.now()), not any([0, 'abc', 1.5, {}, []])])