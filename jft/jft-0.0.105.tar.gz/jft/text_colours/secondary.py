from jft.text_colours.dark.magenta import f as magenta
f = lambda μ: magenta(μ)
t = lambda: '\x1b[0;35mxyz\x1b[0;0m' == f('xyz')
