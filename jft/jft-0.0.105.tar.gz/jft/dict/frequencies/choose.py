from random import choices

def f(x):
  Σ = sum(x.values())
  _K, _P = zip(*{k: x[k]/Σ for k in x}.items())
  return choices(_K, weights=_P)[0]

def t():
  n = 1000
  x = {'A': 9, 'B': 1}
  z = [f(x) for _ in range(n)]
  z_freq = {_: len([i for i in z if i == _]) for _ in 'AB'}
  return all([round(z_freq['A']/n, 1)==0.9, round(z_freq['B']/n, 1)==0.1])
