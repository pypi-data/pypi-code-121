from jft.strings.contain.version import f as k
from jft.pip.version.to_str import f as make_v_str

f = lambda v, Λ: [(f'version = {make_v_str(v)}' if k(λ) else λ) for λ in Λ]

v = {'major': 4, 'minor': 5, 'patch': 6}

t = lambda: all([
  ['version = 4.5.6', '.'] == f(v, ['version = 1.2.3', '.']), [] == f({}, []),
  ['.', 'version = 4.5.6'] == f(v, ['.', 'version = 1.2.3']), [] == f(v, []),
])