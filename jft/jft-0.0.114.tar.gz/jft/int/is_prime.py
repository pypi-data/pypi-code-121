from math import sqrt
from jft.text_colours.bright.cyan import f as cyan

f = lambda x: all([x%i for i in range(2, x)])

def t():
  for (x, y) in [
    (180,False),
    (15, False),
    (2, True),
    (3, True),
    (4, False),
    (5, True),
    (6, False),
    (7, True),
    (8, False),
    (9, False),
    (10, False),
    (11, True),
    (12, False),
    (13, True),
    (14, False),
    (16, False),
    (17, True),
  ]:
    z = f(x)
    if z != y:
      print(cyan(f'x: {x}'))
      print(cyan(f'y: {y}'))
      print(cyan(f'z: {z}'))
      print()
      return False
  return True
