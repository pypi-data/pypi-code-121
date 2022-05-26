from math import isnan
from numpy import nan

def f(x):
  if isinstance(x, str): return x
  return None if isnan(x) else x

def t():
  return f(nan) == None
