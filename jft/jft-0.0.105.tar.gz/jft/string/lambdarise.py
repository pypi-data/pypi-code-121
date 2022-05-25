from jft.string.single_line_function.to_lambda_str import f as to_λ_str

def f(x):
  y = '\n'.join([to_λ_str(λ) for λ in x.split('\n')])
  return len(x) > len(y), y

def t():
  change_made, z = f('\n'.join([
    "def f(x): return x*x",
    "def t():",
    "  y = f(4)",
    "  return y==16",
    "if __name__=='__main__': print(t())",
  ]))
  return all([change_made, '\n'.join([
    "f = lambda x: x*x",
    "def t():",
    "  y = f(4)",
    "  return y==16",
    "if __name__=='__main__': print(t())",
  ]) == z])

if __name__=='__main__': t()