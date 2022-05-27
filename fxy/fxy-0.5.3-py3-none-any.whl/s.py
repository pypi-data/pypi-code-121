# Symbolics and Calculus

try:
    import sympy; exec(sympy.interactive.session.preexec_source)
    a, b, c = symbols('a b c')
except:
    pass

try:
    from sympy.plotting import plot3d
except:
    pass

# Plotting is included
