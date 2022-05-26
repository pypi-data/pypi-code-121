from random import randint

def f(x):
  for n in range(1, 81):
    x = x.replace('\n'+(' '*n)+'\n', '\n\n') 
  return x

t = lambda: all([
  '\n\n' == f('\n \n'),
  '\n\n' == f('\n'+' '*randint(2, 80) +'\n')
])