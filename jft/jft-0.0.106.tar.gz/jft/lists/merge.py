f = lambda Λ_a, Λ_b: Λ_a + [λ_b for λ_b in Λ_b if λ_b not in set(Λ_a)]
t = lambda: all([
  [] == f([], []),
  list('abcdef') == f(list('abc'), list('def')),
  list('abcd') == f(list('abc'), list('bcd')),
])