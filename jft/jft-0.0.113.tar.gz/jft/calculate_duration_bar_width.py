from jft.log_2 import f as log_2
from math import ceil
w_max = 23
f = lambda t_ms: 0 if t_ms <= 0 else min(max(0, ceil(log_2(t_ms))), w_max)
t = lambda: all([
  0 == f(-1),
  0 == f(0),
  *[_ == f(2**_) for _ in range(24)],
  23 == f(9000000),
])