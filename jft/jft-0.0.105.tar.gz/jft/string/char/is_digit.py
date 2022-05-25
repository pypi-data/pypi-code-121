from string import digits
# is_digit
f = lambda x: x in digits
t = lambda: all([f(str(_)) for _ in range(10)]) and not f('x')