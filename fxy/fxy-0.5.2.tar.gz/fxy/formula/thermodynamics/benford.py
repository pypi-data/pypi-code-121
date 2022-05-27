from sympy import symbols
from sympy import log

n = symbols('digits')

n_probability = log(n + 1) - log(n)
