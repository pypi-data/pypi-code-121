from string import printable

# strip_unprintable
f = lambda ζ: ''.join(filter(lambda z: z in printable, ζ))
def t(): return True # TODO: Fix this test