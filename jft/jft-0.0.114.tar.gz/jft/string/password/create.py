from string import ascii_lowercase as l
from string import ascii_uppercase as u
from string import digits as d
from string import punctuation as p
from random import choice
from random import shuffle
from jft.text_colours.tgfr import f as tgfr

def f(n=8):
  base = [choice(_) for _ in [d, l, p, u]]
  extra = [choice(l+u+d+p) for _ in range(n-len(base))]
  result = base + extra
  shuffle(result)
  return ''.join(result)

def t():
  z_0 = f()
  z_1 = f()
  
  if not isinstance(z_0, str): return False
  has_an_upper = any([c in u for c in z_0])
  has_a_lower = any([c in l for c in z_0])
  has_digits = any([c in d for c in z_0])
  has_punctuation = any([c in p for c in z_0])
  len_8_or_more = len(z_0) >= 8
  is_different_from_last = z_0 != z_1

  
  result = all([
    has_an_upper,
    has_a_lower,
    has_digits,
    has_punctuation,
    len_8_or_more,
    is_different_from_last
  ])

  if not result:
    print(f'z_0: {tgfr(z_0)}')
    print(f'z_1: {tgfr(z_1)}')
    print(f'has_an_upper: {tgfr(has_an_upper)}')
    print(f'has_a_lower: {tgfr(has_a_lower)}')
    print(f'has_digits: {tgfr(has_digits)}')
    print(f'has_punctuation: {tgfr(has_punctuation)}')
    print(f'len_8_or_more: {tgfr(len_8_or_more)}')
    print(f'is_different_from_last: {tgfr(is_different_from_last)}')
    return False

  return True