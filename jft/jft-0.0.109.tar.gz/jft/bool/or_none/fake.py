from random import choice
from jft.bool.or_none.is_a import f as is_a_bool_or_none
f = lambda: choice([True, False, None])
t = lambda: is_a_bool_or_none(f())
