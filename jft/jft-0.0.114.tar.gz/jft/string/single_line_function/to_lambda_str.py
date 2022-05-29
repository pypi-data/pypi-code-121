from jft.string.single_line_function.is_a import f as is_1_line_fn

def f(x):
  if is_1_line_fn(x):
    name = x[(x.find('def ') + len('def ')):x.find('(', x.find('def '))] 
    args = x[(x.find('(') + len('(')):x.find(')', x.find('('))] 
    body = x[(x.find('): return ') + len('): return ')):] 
    return f'{name} = lambda {args}: {body}'
  return x

t = lambda: 'foo = lambda x: x*x\n' == f('def foo(x): return x*x\n')

if __name__ == '__main__': print(t())