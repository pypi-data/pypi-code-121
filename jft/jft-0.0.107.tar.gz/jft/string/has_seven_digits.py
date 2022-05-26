from jft.string.digits.remove import f as remove_digits
f = lambda x: len(x) - len(remove_digits(x)) == 7
t = lambda: all([not f(''), f('z1234567'), not f('z12345678')])
