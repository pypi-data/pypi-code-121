from jft.system.git.commit.run import f as commit
from jft.nop import f as nop

f = lambda tests_ok, app_ok, f_a=commit, f_b=nop: (
  f_a if tests_ok and app_ok else f_b
)()

_f_a = lambda: 'f'
_f_b = lambda: 'g'
_t = True
_f = False

t = lambda: all([
  f(_t, _t, _f_a, _f_b) == 'f',
  f(_f, _t, _f_a, _f_b) == 'g',
  f(_t, _f, _f_a, _f_b) == 'g',
  f(_f, _f, _f_a, _f_b) == 'g',
])
