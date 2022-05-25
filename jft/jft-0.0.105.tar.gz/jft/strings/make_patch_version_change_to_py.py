from jft.pip.version.to_str import f as make_v_str
from jft.string.contains.version import f as k

f = lambda v, Λ: [(f"  version='{make_v_str(v)}'," if k(λ) else λ) for λ in Λ]

v = {'major': 4, 'minor': 5, 'patch': 6}

t = lambda: all([
  [] == f({}, []),
  [] == f(v, []),
  ["  version='4.5.6',", '.\n'] == f(v, ["version = '1.2.3'\n", '.\n']),
  ['.\n', "  version='4.5.6',"] == f(v, ['.\n', "version = '1.2.3'\n"]),
])