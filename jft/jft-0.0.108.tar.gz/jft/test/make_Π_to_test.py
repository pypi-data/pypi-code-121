_Π = ['./a.py', './b.py', './c.py']
_test_all  = False
_prev = {'./b.py': 32481.8, './c.py': 32497.3}
_last_mods = {'./a.py': 97551.0, './b.py': 32481.8, './c.py': 32497.3}

def f(Π, test_all, prev, last_mods): return (
  Π.copy() if test_all else [
    π for π in Π if (
      (prev[π] if π in prev else 0)
      !=
      (last_mods[π] if π in last_mods else 0)
    )
  ]
) or Π.copy()

t = lambda: ['./a.py'] == f(_Π, _test_all, _prev, _last_mods)
