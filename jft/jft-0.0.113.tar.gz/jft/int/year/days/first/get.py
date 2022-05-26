from datetime import date as dt
from random import randint

f = lambda year: dt(year, 1, 1)

def t():
  y = randint(1900, 2100)
  return f(y) == dt(y, 1, 1)
