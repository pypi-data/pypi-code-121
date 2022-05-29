def f(x, y):
  if x == y: return (True, 'Match')
  if len(x) < len(y): return (False, f'len(x): {len(x)} < len(y): {len(y)}')
  if len(x) > len(y): return (False, f'len(x): {len(x)} > len(y): {len(y)}')
  
  for i in range(len(x)):
    if x[i] != y[i]: return (False, f"x[{i}]: '{x[i]}' != y[{i}]: '{y[i]}'", i)
  
  return (False, "Unknown mismatch")
  
t = lambda: all([
  (True, 'Match') == f('abc', 'abc'),
  (False, 'len(x): 3 < len(y): 4') == f('abc', 'abcd'),
  (False, 'len(x): 4 > len(y): 3') == f('abcd', 'abc'),
  (False, "x[1]: 'x' != y[1]: 'y'", 1) == f('axc', 'ayc'),
])
