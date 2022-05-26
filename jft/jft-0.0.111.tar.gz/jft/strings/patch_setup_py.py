from jft.strings.contain.version import f as k
from jft.pip.version.to_str import f as make_v_str

f = lambda v, Λ: [(f"  version='{make_v_str(v)}'," if k(λ) else λ) for λ in Λ]

v = {'major': 4, 'minor': 5, 'patch': 6}

def t():
  for (expectation, observation) in [
    ([], f({}, [])),
    ([], f(v, [])),
    (["  version='4.5.6',", '.'], f(v, ["  version='x.x.x',", '.'])),
    (['.', "  version='4.5.6',"], f(v, ['.', "  version='x.x.x',"])),
  ]:
    if expectation != observation:
      print(f'expectation: {expectation}')
      print(f'observation: {observation}')
      return False
  return True