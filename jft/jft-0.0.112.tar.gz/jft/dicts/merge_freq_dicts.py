def f(a, b):
  d_ab = {k_a: a[k_a] for k_a in a}
  for k_b in b:
    if k_b in d_ab:
      for k in b[k_b]:
        if k in d_ab[k_b]:
          d_ab[k_b][k] += b[k_b][k]
        else:
          d_ab[k_b][k] = b[k_b][k]
    else:
      d_ab[k_b] = b[k_b]
  return d_ab

def t():
  d1 = {'aa': {'a': 1, 'b': 2, '!': 3}, 'ab': {'a': 4, 'b': 5, '!': 6}}
  d2 = {'ab': {'a': 7, 'b': 8, '!': 9}, 'ba': {'a': 1, 'b': 2, '!': 3}}

  d3 = {'aa': {'c': 2}}
  d4 = {'aa': {'d': 1}}
  return all([
    f(d1, d2) == {
      'aa': {'a': 1, 'b': 2, '!': 3},
      'ab': {'a': 11, 'b': 13, '!': 15},
      'ba': {'a': 1, 'b': 2, '!': 3},
    },
    f(d3, d4) == {'aa': {'c': 2}, 'aa': {'c': 2, 'd': 1}},
  ])