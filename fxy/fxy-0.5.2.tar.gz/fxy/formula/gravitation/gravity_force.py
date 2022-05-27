from sympy import symbols, sympify
from scipy import constants as const

m1, m2, d = symbols('mass1, mass2, distance')

F_gravity = const.G * ((m1*m2) / d**2)
