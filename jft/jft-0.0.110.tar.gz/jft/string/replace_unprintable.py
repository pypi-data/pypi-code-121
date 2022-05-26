from string import printable

# replace_unprintable
f = lambda ζ: ''.join([z if z in printable else '*' for z in ζ])
def t(): return True # TODO: Fix this test