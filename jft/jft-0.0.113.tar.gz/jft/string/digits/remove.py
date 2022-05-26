from jft.string.chars.remove import f as remove_characters
f = lambda x: remove_characters({'str': x, 'chars':'0123456789'})
t = lambda: all([f('abc') == 'abc', f('a1b2c3') == 'abc', f('123') == ''])
