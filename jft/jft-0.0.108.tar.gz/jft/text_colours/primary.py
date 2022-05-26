from jft.text_colours.bright.blue import f as b_blue
f = lambda μ: b_blue(μ)
t = lambda: '\x1b[1;34mxyz\x1b[0;0m' == f('xyz')