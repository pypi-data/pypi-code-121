f = lambda d, k, v_if_k_not_in_d: d[k] if k in d else v_if_k_not_in_d
t = lambda: all([
  f({'a': 0}, 'a', '!') == 0,
  f({'a': 1}, 'a', '@') == 1,
  f({'a': 1}, 'b', set()) == set()
])