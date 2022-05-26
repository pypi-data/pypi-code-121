from random import randint

def f(x):
  for n in range(0, 81):
    x = x.replace(
      '\n'+(' '*n)+'#',
      '\n\n'+(' '*n)+'#'
    )
  return x

def t():
  n = randint(2, 80)
  return all([
    '\n\n  #' == f('\n  #'),
    '\n\n#' == f('\n#'),
    '\n\n'+' '*n+'#' == f('\n'+' '*n +'#')
  ])
