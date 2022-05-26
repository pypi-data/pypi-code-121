from jft.string.to_cond_freq_dict import f as to_cond_freq_dict
from jft.dicts.merge_freq_dicts import f as merge_freq_dicts

def f(x):
  d = {}
  for x_i in x:
    _d = to_cond_freq_dict(x_i)
    d = merge_freq_dicts(d, _d)
  return d

def t():
  z = f(['aac', 'aac', 'aad', 'aae', 'abc', 'abd', 'abe'])
  y = {'aa': {'c': 2, 'd': 1, 'e': 1}, 'ab': {'c': 1, 'd': 1, 'e': 1}}
  return z == y
