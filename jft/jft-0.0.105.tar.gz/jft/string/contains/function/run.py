Γ = [
  'def f(',
  'def f():',
  'def f(x):',
  'def f(a, b):',
  'f = lambda a, b:',
  'f = lambda x:',
  'f = lambda:',
  'f = lambda',
]

f = lambda x: any([λ.startswith(γ) for γ in Γ for λ in x.split('\n')])

t = lambda: all([
  f("f = lambda x:"), not f("t = lambda:"),
  f("f = lambda x:\nt = lambda:"), not f(""),
])
