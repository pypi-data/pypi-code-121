from jft.string.contains.λ import f as contains_lambda

def f(x):
  lines_containing_lambda = [λ for λ in x.split('\n') if contains_lambda(λ)]
  if lines_containing_lambda:
    for λ in lines_containing_lambda:
      x = x.replace(λ, '\n'+λ)
    return x
  else:
    return x

t = lambda: all([
  '\nf = lambda self: 0' == f('f = lambda self: 0'),
  '\nrun = lambda ' == f('run = lambda '),
  '\nrun = lambda:' == f('run = lambda:'),
  '\ntest = lambda ' == f('test = lambda '),
  '\ntest = lambda:' == f('test = lambda:'),
])
