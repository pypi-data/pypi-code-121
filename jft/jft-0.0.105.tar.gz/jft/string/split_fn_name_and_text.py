from jft.find_first_parenthesis import f as find_first_parenthesis

fn_name_and_text = '\n'.join(['def foo(x):', '  return x**2', ''])

t = lambda: ('foo', "(x):\n  return x**2\n") == f(fn_name_and_text)

def f(x):
  first_parenthesis = find_first_parenthesis(x)
  return (x[4:first_parenthesis], x[first_parenthesis:])
