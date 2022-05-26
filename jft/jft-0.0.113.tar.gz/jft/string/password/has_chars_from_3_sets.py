from jft.bools.count_true import f as count_true
from jft.string.has_digit import f as has_09
from jft.string.has_lowercase import f as has_az
from jft.string.has_uppercase import f as has_AZ
from jft.string.has_other_char import f as has_other

f = lambda x: count_true([has_09(x), has_az(x), has_AZ(x), has_other(x)]) >= 3

t = lambda: all([
  not f('12345678'),
  not f('abcdefgh'),
  not f('ABCDEFGH'),
  not f('!@#$%^&*'),
  not f('12345678'),
  not f('1234efgh'),
  not f('abcdEFGH'),
  not f('ABCD%^&*'),
  f('12cdEF^&'),
])
